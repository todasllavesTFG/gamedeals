from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.games import Game
from app.models.prices import Price
from app.models.price_history import PriceHistory
from app.services.images import game_image_url


def get_unified_game(db: Session, game_id: int) -> dict | None:
    game = (
        db.query(Game)
        .options(
            joinedload(Game.prices).joinedload(Price.store),
        )
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        return None

    all_time_low = (
        db.query(func.min(PriceHistory.price))
        .filter(PriceHistory.game_id == game_id)
        .scalar()
    )

    prices_list = []
    best_price_entry = None

    for p in game.prices:
        if best_price_entry is None or p.current_price < best_price_entry.current_price:
            best_price_entry = p

    for p in game.prices:
        prices_list.append({
            "store_name": p.store.name,
            "store_logo": p.store.logo_url,
            "original_price": p.original_price,
            "current_price": p.current_price,
            "discount_percent": p.discount_percent,
            "deal_url": p.deal_url,
            "last_updated": p.last_updated.isoformat() if p.last_updated else None,
            "is_best_price": p.id == best_price_entry.id if best_price_entry else False,
        })

    best_price = None
    if best_price_entry:
        best_price = {
            "store_name": best_price_entry.store.name,
            "current_price": best_price_entry.current_price,
            "discount_percent": best_price_entry.discount_percent,
            "deal_url": best_price_entry.deal_url,
        }

    return {
        "id": game.id,
        "title": game.title,
        "slug": game.slug,
        "description": game.description,
        "image_url": game_image_url(game.image_url, game.steam_app_id),
        "genre": game.genre,
        "platform": game.platform,
        "metacritic_score": game.metacritic_score,
        "rawg_id": game.rawg_id,
        "steam_app_id": game.steam_app_id,
        "prices": prices_list,
        "best_price": best_price,
        "all_time_low": all_time_low,
    }
