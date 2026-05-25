from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("game_id", "store_id", name="uq_price_game_store"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    original_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deal_url: Mapped[str | None] = mapped_column(String, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="prices")
    store = relationship("Store", back_populates="prices")
