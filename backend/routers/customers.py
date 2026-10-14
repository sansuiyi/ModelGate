from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models import CustomerProfile, CustomerConstraints, CustomerPerformance
from backend.database import list_customers, get_customer, save_customer, delete_customer

router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerProfileUpdate(BaseModel):
    """Partial update model for customer profiles."""
    objective: str | None = None
    use_case: str | None = None
    constraints: CustomerConstraints | None = None
    performance: CustomerPerformance | None = None
    routing_preferences: dict[str, list[str]] | None = None
    warnings: list[str] | None = None


@router.get("", response_model=list[CustomerProfile])
def get_customers():
    return list_customers()


@router.get("/{customer_id}", response_model=CustomerProfile)
def get_customer_by_id(customer_id: str):
    profile = get_customer(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    return profile


@router.post("", response_model=CustomerProfile)
def create_customer(profile: CustomerProfile):
    save_customer(profile)
    return profile


@router.put("/{customer_id}", response_model=CustomerProfile)
def update_customer(customer_id: str, update: CustomerProfileUpdate):
    """Update specific fields of a customer profile."""
    profile = get_customer(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Apply partial updates
    if update.objective is not None:
        profile.objective = update.objective
    if update.use_case is not None:
        profile.use_case = update.use_case
    if update.constraints is not None:
        profile.constraints = update.constraints
    if update.performance is not None:
        profile.performance = update.performance
    if update.routing_preferences is not None:
        profile.routing_preferences = update.routing_preferences
    if update.warnings is not None:
        profile.warnings = update.warnings

    save_customer(profile)
    return profile


@router.delete("/{customer_id}")
def remove_customer(customer_id: str):
    if not delete_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "deleted", "customer_id": customer_id}
