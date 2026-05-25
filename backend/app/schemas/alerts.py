from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    game_id: int
    target_price: float = Field(..., gt=0, description="Precio objetivo en euros")


class AlertUpdate(BaseModel):
    target_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class AlertOut(BaseModel):
    id: int
    game_id: int
    target_price: float
    is_active: bool
    is_triggered: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    # Campos enriquecidos (calculados en el router)
    game_title: Optional[str] = None
    game_image: Optional[str] = None
    current_best_price: Optional[float] = None
    best_store_name: Optional[str] = None

    model_config = {"from_attributes": True}
