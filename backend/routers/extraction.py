from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.models import ExtractionRequest, CustomerProfile
from backend.services.extractor import extract_profile
from backend.database import save_customer

router = APIRouter(tags=["extraction"])


@router.post("/extract", response_model=CustomerProfile)
async def extract_from_json(request: ExtractionRequest):
    try:
        profile = await extract_profile(
            customer_name=request.customer_name,
            contract_text=request.contract_text,
            custom_instructions=request.custom_instructions,
        )
        save_customer(profile)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/extract/upload", response_model=CustomerProfile)
async def extract_from_file(
    file: UploadFile = File(...),
    customer_name: str = Form(...),
    custom_instructions: str = Form(""),
):
    try:
        content = await file.read()
        contract_text = content.decode("utf-8", errors="replace")

        profile = await extract_profile(
            customer_name=customer_name,
            contract_text=contract_text,
            custom_instructions=custom_instructions,
        )
        save_customer(profile)
        return profile
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not read file. Please upload a text file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
