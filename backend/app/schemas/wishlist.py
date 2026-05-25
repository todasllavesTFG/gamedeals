from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GameInWishlist(BaseModel):
    id: int
    title: str
    slug: str
    image_url: str | None = None
    metacritic_score: int | None = None

    model_config = ConfigDict(from_attributes=True)


class BestPriceInfo(BaseModel):
    store_name: str
    current_price: float
    discount_percent: int | None = None
    deal_url: str | None = None


class WishlistItemOut(BaseModel):
    id: int
    game_id: int
    added_at: datetime
    game: GameInWishlist
    best_price: BestPriceInfo | None = None

    model_config = ConfigDict(from_attributes=True)
