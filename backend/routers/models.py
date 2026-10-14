import httpx
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database import get_global_models, update_global_model, add_global_model, remove_global_model
from backend.config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["models"])


class ModelUpdate(BaseModel):
    enabled: bool
    description: str = ""


class ModelCreate(BaseModel):
    model_name: str
    provider: str
    openrouter_id: str = ""
    tier: str = "medium"
    cost_per_m_input: float = 1.0
    cost_per_m_output: float = 5.0
    avg_latency_ms: int = 500
    regions: list[str] = ["US"]
    max_context: int = 128000
    description: str = ""


@router.get("")
def list_models():
    return get_global_models()


@router.post("")
def create_model(model: ModelCreate):
    model_data = model.model_dump()
    if not model_data.get("openrouter_id"):
        model_data["openrouter_id"] = model_data["model_name"]
    add_global_model(model_data)
    return {"status": "created", "model_name": model.model_name}


@router.delete("/{model_name}")
def delete_model(model_name: str):
    removed = remove_global_model(model_name)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    return {"status": "deleted", "model_name": model_name}


@router.put("/{model_name}")
def toggle_model(model_name: str, update: ModelUpdate):
    update_global_model(model_name, update.enabled, update.description)
    return {"status": "updated", "model_name": model_name, "enabled": update.enabled}


@router.get("/openrouter/catalog")
async def openrouter_catalog(q: str = ""):
    """Browse available models from OpenRouter's catalog."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            )
            resp.raise_for_status()
        data = resp.json().get("data", [])

        models = []
        for m in data:
            model_id = m.get("id", "")
            name = m.get("name", model_id)
            pricing = m.get("pricing", {})

            # Filter by search query
            if q and q.lower() not in name.lower() and q.lower() not in model_id.lower():
                continue

            prompt_cost = float(pricing.get("prompt", "0")) * 1_000_000
            completion_cost = float(pricing.get("completion", "0")) * 1_000_000

            models.append({
                "id": model_id,
                "name": name,
                "context_length": m.get("context_length", 0),
                "cost_per_m_input": round(prompt_cost, 4),
                "cost_per_m_output": round(completion_cost, 4),
                "provider": model_id.split("/")[0] if "/" in model_id else "unknown",
            })

        # Sort by name
        models.sort(key=lambda x: x["name"])
        return models[:100]  # Cap at 100 results
    except Exception as e:
        logger.error(f"Failed to fetch OpenRouter catalog: {e}")
        return []
