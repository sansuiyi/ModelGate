import json
import time
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.models import ChatCompletionRequest, CustomerProfile
from backend.database import get_customer, save_request_log
from backend.services.router_engine import route
from backend.services.provider_registry import get_model_info
from backend.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    PLAYGROUND_MODEL_SIMPLE,
    PLAYGROUND_MODEL_MEDIUM,
    PLAYGROUND_MODEL_COMPLEX,
    DEEPSEEK_DISABLE_THINKING,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playground", tags=["playground"])

# ============================================================================
# 测试台"临时回复模型"映射（按复杂度）。
# 仅测试台使用，合同解析走同一条 DeepSeek 直连，正式代理仍走 OPENROUTER_*（方舟）。
#   simple  -> deepseek-flash
#   medium  -> deepseek-flash（即 V4.1 Flash）
#   complex -> deepseek-v4-pro
# ============================================================================
PLAYGROUND_REPLY_MODELS = {
    "simple": PLAYGROUND_MODEL_SIMPLE,
    "medium": PLAYGROUND_MODEL_MEDIUM,
    "complex": PLAYGROUND_MODEL_COMPLEX,
}


@router.post("/chat")
async def playground_chat(customer_id: str, request: ChatCompletionRequest):
    """测试台专用：路由决策按客户合同展示，实际回复用 DeepSeek 直连模型。

    1. 用路由引擎按客户合同 routing_preferences 选出目标模型（仅用于展示）。
    2. 实际调用按复杂度映射到 DeepSeek 模型拿回答（默认关闭思考模式）。
    """
    profile: CustomerProfile | None = get_customer(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found")
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY not configured")

    user_prompt = ""
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            user_prompt = msg.get("content", "")
            break
    if not user_prompt:
        raise HTTPException(status_code=400, detail="No user message found")

    # 1) 路由决策（按客户合同）—— 仅用于展示
    classify_start = time.time()
    decision = route(profile, user_prompt, tier_override=None)
    classify_ms = int((time.time() - classify_start) * 1000)

    # 2) 实际调用：按复杂度选 DeepSeek 模型
    reply_model = PLAYGROUND_REPLY_MODELS.get(decision.classification, PLAYGROUND_REPLY_MODELS["medium"])

    status = "success"
    ttft_ms = 0
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": reply_model,
                    "messages": request.messages,
                    "temperature": request.temperature,
                    **({"max_tokens": request.max_tokens} if request.max_tokens else {}),
                    **({"thinking": {"type": "disabled"}} if DEEPSEEK_DISABLE_THINKING else {}),
                },
            )
            ttft_ms = int((time.time() - start_time) * 1000)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        status = "error"
        logger.error(f"Playground reply model error: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=502, detail=f"Reply model error: {e.response.status_code}")
    except httpx.RequestError as e:
        status = "error"
        logger.error(f"Playground reply request failed: {e}")
        raise HTTPException(status_code=502, detail="Failed to reach reply model")

    latency_ms = int((time.time() - start_time) * 1000)
    result = response.json()
    usage = result.get("usage", {})
    input_tokens = usage.get("prompt_tokens", len(user_prompt.split()) * 2)
    output_tokens = usage.get("completion_tokens", 100)

    # 落日志（与正式代理一致，便于统计）
    log_entry = {
        "customer_id": customer_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_preview": user_prompt[:200],
        "classification": decision.classification,
        "selected_provider": "deepseek",
        "selected_model": reply_model,
        "reason": decision.reason,
        "latency_ms": latency_ms,
        "estimated_cost": 0.0,
        "tokens_used": input_tokens + output_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "ttft_ms": ttft_ms,
        "status": status,
        "candidates_considered": decision.candidates_considered,
        "candidates_eliminated": decision.candidates_eliminated,
    }
    save_request_log(log_entry)

    # 按客户合同选中的模型计算成本（合同定价）
    contract_model_info = get_model_info(decision.selected_model) or {}
    contract_in_price = float(contract_model_info.get("cost_per_m_input", 0) or 0)
    contract_out_price = float(contract_model_info.get("cost_per_m_output", 0) or 0)
    contract_cost = (input_tokens / 1_000_000) * contract_in_price + (output_tokens / 1_000_000) * contract_out_price

    resp = JSONResponse(content=result)
    routing_meta = {
        **decision.model_dump(),
        "latency_ms": latency_ms,
        "ttft_ms": ttft_ms,
        "classify_ms": classify_ms,
        "cost": round(contract_cost, 6),
        "contract_cost": round(contract_cost, 6),
        "contract_cost_per_m_input": contract_in_price,
        "contract_cost_per_m_output": contract_out_price,
        "contract_avg_latency_ms": contract_model_info.get("avg_latency_ms", 0),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        # 展示层用的合同模型
        "contract_selected_model": decision.selected_model,
        "contract_selected_provider": decision.selected_provider,
        # 实际回复用的默认方舟模型
        "reply_model": reply_model,
    }
    resp.headers["X-Routing-Decision"] = json.dumps(routing_meta)
    resp.headers["X-Model-Used"] = reply_model
    resp.headers["X-Classification"] = decision.classification
    resp.headers["X-Latency-Ms"] = str(latency_ms)
    resp.headers["X-TTFT-Ms"] = str(ttft_ms)
    resp.headers["X-Classify-Ms"] = str(classify_ms)
    return resp
