import io
import logging
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.agent import run_react_agent
from backend.config import MAX_CONTRACT_CHARS
from backend.models import CustomerProfile, ExtractionRequest
from backend.services.extractor import extract_profile
from backend.services.profile_policy import normalize_warnings, sanitize_routing_preferences
from backend.database import save_customer

logger = logging.getLogger(__name__)

router = APIRouter(tags=["extraction"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def _decode_text(data: bytes) -> str:
    """文本文件优先按 UTF-8 解码，失败再尝试 GB18030（兼容中文合同）。"""
    for encoding in ("utf-8", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _pdf_to_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise HTTPException(
            status_code=500, detail="PDF parsing is unavailable; upload a .txt or .md file."
        ) from e

    try:
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}") from e


def _contract_text_from_upload(content: bytes, suffix: str) -> str:
    if suffix == ".pdf":
        return _pdf_to_text(content)
    return _decode_text(content)


def _log_extraction(profile: CustomerProfile) -> None:
    m = profile.extraction or {}
    logger.info(
        "Contract extraction customer=%s mode=%s calls=%s iterations=%s tokens=%s/%s "
        "cost_usd=%s elapsed_ms=%s fallback=%s",
        profile.customer_id,
        m.get("mode"),
        m.get("llm_calls"),
        m.get("iterations"),
        m.get("prompt_tokens"),
        m.get("completion_tokens"),
        m.get("estimated_cost_usd"),
        m.get("elapsed_ms"),
        m.get("fallback_from"),
    )


async def _extract_contract(
    customer_name: str, contract_text: str, custom_instructions: str
) -> CustomerProfile:
    """统一抽取入口：优先 ReAct Agent，失败回退单次抽取，再统一做合规清理。"""
    if len(contract_text) > MAX_CONTRACT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Contract is too long ({len(contract_text)} chars). "
                f"Limit is {MAX_CONTRACT_CHARS} chars; split the contract before extraction."
            ),
        )

    try:
        profile = await run_react_agent(
            contract_text=contract_text,
            customer_name=customer_name,
            custom_instructions=custom_instructions,
        )
    except Exception as e:
        logger.warning(f"ReAct extraction failed, falling back to single-shot: {e!r}")
        profile = await extract_profile(
            customer_name=customer_name,
            contract_text=contract_text,
            custom_instructions=custom_instructions,
        )
        metrics = dict(profile.extraction or {})
        metrics["fallback_from"] = "react"
        metrics["fallback_reason"] = f"{type(e).__name__}: {e}"[:300]
        profile.extraction = metrics

    # 所有入库路径统一做合规清理与 warning 归一化（幂等）
    sanitize_routing_preferences(profile)
    normalize_warnings(profile)
    _log_extraction(profile)
    return profile


@router.post("/extract", response_model=CustomerProfile)
async def extract_from_json(request: ExtractionRequest):
    try:
        profile = await _extract_contract(
            customer_name=request.customer_name,
            contract_text=request.contract_text,
            custom_instructions=request.custom_instructions,
        )
        save_customer(profile)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/extract/react", response_model=CustomerProfile)
async def extract_react(request: ExtractionRequest):
    """显式走 Agent 抽取；行为与 /extract 一致（内部已含单次抽取回退）。"""
    return await extract_from_json(request)


@router.post("/extract/upload", response_model=CustomerProfile)
async def extract_from_file(
    file: UploadFile = File(...),
    customer_name: str = Form(...),
    custom_instructions: str = Form(""),
):
    try:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Upload a .txt, .md or .pdf file.",
            )

        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({len(content)} bytes). Limit is {MAX_UPLOAD_BYTES} bytes.",
            )

        contract_text = _contract_text_from_upload(content, suffix)
        if not contract_text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in the uploaded file.")

        profile = await _extract_contract(
            customer_name=customer_name,
            contract_text=contract_text,
            custom_instructions=custom_instructions,
        )
        save_customer(profile)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
