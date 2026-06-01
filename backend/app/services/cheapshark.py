import logging
from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.models.games import Game
from app.models.prices import Price
from app.models.price_history import PriceHistory
from app.models.stores import Store
from app.services.images import steam_header_image_url

logger = logging.getLogger(__name__)

CHEAPSHARK_API = "https://www.cheapshark.com/api/1.0"

STORE_MAP = {
    "1": "Steam",
    "7": "GOG",
    "15": "Fanatical",
    "11": "Humble Bundle",
}


async def fetch_deals_from_api(
    page: int = 0,
    page_size: int = 20,
    sort_by: str = "Deal Rating",
    min_price: float = 0,
    max_price: float = 50,
) -> list[dict]:
    params = {
        "pageNumber": page,
        "pageSize": page_size,
        "sortBy": sort_by,
        "lowerPrice": min_price,
        "upperPrice": max_price,
        "storeID": ",".join(STORE_MAP.keys()),
    }
    headers = {"User-Agent": "GameDeals/1.0 (TFG DAM project)"}
    async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
        response = await client.get(f"{CHEAPSHARK_API}/deals", params=params)
        response.raise_for_status()
        return response.json()


def _get_or_create_store(db: Session, store_id_cs: str) -> Store | None:
    store_name = STORE_MAP.get(store_id_cs)
    if not store_name:
        return None

    store = db.query(Store).filter_by(name=store_name).first()
    if not store:
        store = Store(
            name=store_name,
            url=f"https://www.cheapshark.com/redirect?dealID=placeholder",
            is_scraper=False,
        )
        db.add(store)
        db.flush()
    return store


def _slugify(title: str) -> str:
    import re
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug


def _get_or_create_game(db: Session, deal: dict) -> Game:
    steam_app_id = deal.get("steamAppID")

    if steam_app_id:
        game = db.query(Game).filter_by(steam_app_id=str(steam_app_id)).first()
        if game:
            if not game.image_url:
                game.image_url = deal.get("thumb") or steam_header_image_url(steam_app_id)
            return game

    slug = _slugify(deal["title"])
    game = db.query(Game).filter_by(slug=slug).first()
    if game:
        if not game.image_url:
            game.image_url = deal.get("thumb") or steam_header_image_url(steam_app_id)
        return game

    game = Game(
        title=deal["title"],
        slug=slug,
        image_url=deal.get("thumb") or steam_header_image_url(steam_app_id),
        metacritic_score=int(deal["metacriticScore"]) if deal.get("metacriticScore") and deal["metacriticScore"] != "0" else None,
        steam_app_id=str(steam_app_id) if steam_app_id else None,
        platform="PC",
    )
    db.add(game)
    db.flush()
    return game


def save_deals_to_db(db: Session, deals: list[dict]) -> dict:
    games_created = 0
    prices_updated = 0
    history_added = 0
    skipped = 0

    for deal in deals:
        try:
            store = _get_or_create_store(db, deal.get("storeID", ""))
            if not store:
                skipped += 1
                continue

            game = _get_or_create_game(db, deal)

            original_price = float(deal["normalPrice"])
            current_price = float(deal["salePrice"])

            if original_price <= 0:
                skipped += 1
                continue

            discount = round(((original_price - current_price) / original_price) * 100)

            existing_price = (
                db.query(Price)
                .filter_by(game_id=game.id, store_id=store.id)
                .first()
            )

            now = datetime.now(UTC)
            deal_url = f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID', '')}"

            if existing_price:
                price_changed = existing_price.current_price != current_price
                existing_price.original_price = original_price
                existing_price.current_price = current_price
                existing_price.discount_percent = discount
                existing_price.deal_url = deal_url
                existing_price.last_updated = now

                if price_changed:
                    history = PriceHistory(
                        game_id=game.id,
                        store_id=store.id,
                        price=current_price,
                        recorded_at=now,
                    )
                    db.add(history)
                    history_added += 1
            else:
                new_price = Price(
                    game_id=game.id,
                    store_id=store.id,
                    original_price=original_price,
                    current_price=current_price,
                    discount_percent=discount,
                    deal_url=deal_url,
                    last_updated=now,
                )
                db.add(new_price)

                history = PriceHistory(
                    game_id=game.id,
                    store_id=store.id,
                    price=current_price,
                    recorded_at=now,
                )
                db.add(history)
                history_added += 1

            prices_updated += 1

            if not existing_price:
                games_created += 1

        except Exception:
            logger.exception("Error procesando deal: %s", deal.get("title", "desconocido"))
            skipped += 1
            continue

    db.commit()

    result = {
        "games_created": games_created,
        "prices_updated": prices_updated,
        "history_added": history_added,
        "skipped": skipped,
        "total_processed": len(deals),
    }
    logger.info("CheapShark sync completado: %s", result)
    return result
