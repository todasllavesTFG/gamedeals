import asyncio
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

STEAM_STORE_API = "https://store.steampowered.com/api"


async def get_app_details(steam_app_id: str) -> dict | None:
    url = f"{STEAM_STORE_API}/appdetails"
    params = {"appids": steam_app_id, "cc": "es", "l": "es"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(3):
                response = await client.get(url, params=params)
                logger.info("Steam appdetails id=%s -> %s", steam_app_id, response.status_code)
                if response.status_code == 429:
                    logger.warning("Steam rate limit, esperando 2s (intento %d)", attempt + 1)
                    await asyncio.sleep(2)
                    continue
                response.raise_for_status()
                break
            else:
                return None

            data = response.json()
            app_data = data.get(str(steam_app_id), {})
            if not app_data.get("success"):
                return None

            info = app_data["data"]
            price_overview = info.get("price_overview")
            if not price_overview:
                return None

            return {
                "name": info.get("name"),
                "short_description": info.get("short_description"),
                "header_image": info.get("header_image"),
                "price": {
                    "currency": price_overview.get("currency", "EUR"),
                    "initial": price_overview["initial"] / 100,
                    "final": price_overview["final"] / 100,
                    "discount_percent": price_overview.get("discount_percent", 0),
                },
            }
    except Exception:
        logger.exception("Error en Steam appdetails para id=%s", steam_app_id)
        return None


async def search_steam_app_id(title: str) -> str | None:
    url = f"{STEAM_STORE_API}/storesearch"
    params = {"term": title, "cc": "es", "l": "es"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            logger.info("Steam search '%s' -> %s", title, response.status_code)
            if response.status_code == 429:
                await asyncio.sleep(2)
                response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if not items:
                return None
            return str(items[0]["id"])
    except Exception:
        logger.exception("Error en Steam search para '%s'", title)
        return None


async def enrich_game_with_steam(db: Session, game_id: int) -> bool:
    game = db.query(Game).filter_by(id=game_id).first()
    if not game:
        return False

    if not game.steam_app_id:
        app_id = await search_steam_app_id(game.title)
        if not app_id:
            return False
        game.steam_app_id = app_id
        db.flush()

    details = await get_app_details(game.steam_app_id)
    if not details or not details.get("price"):
        return False

    game.image_url = details.get("header_image") or game.image_url or steam_header_image_url(game.steam_app_id)

    steam_store = db.query(Store).filter_by(name="Steam").first()
    if not steam_store:
        steam_store = Store(
            name="Steam",
            url="https://store.steampowered.com",
            is_scraper=False,
        )
        db.add(steam_store)
        db.flush()

    price_data = details["price"]
    original_price = price_data["initial"]
    current_price = price_data["final"]
    discount = price_data["discount_percent"]

    existing_price = (
        db.query(Price)
        .filter_by(game_id=game.id, store_id=steam_store.id)
        .first()
    )

    now = datetime.now(UTC)
    deal_url = f"https://store.steampowered.com/app/{game.steam_app_id}"

    if existing_price:
        price_changed = existing_price.current_price != current_price
        existing_price.original_price = original_price
        existing_price.current_price = current_price
        existing_price.discount_percent = discount
        existing_price.deal_url = deal_url
        existing_price.last_updated = now

        if price_changed:
            db.add(PriceHistory(
                game_id=game.id,
                store_id=steam_store.id,
                price=current_price,
                recorded_at=now,
            ))
    else:
        db.add(Price(
            game_id=game.id,
            store_id=steam_store.id,
            original_price=original_price,
            current_price=current_price,
            discount_percent=discount,
            deal_url=deal_url,
            last_updated=now,
        ))
        db.add(PriceHistory(
            game_id=game.id,
            store_id=steam_store.id,
            price=current_price,
            recorded_at=now,
        ))

    db.commit()
    logger.info("Juego '%s' enriquecido con Steam (app_id=%s, precio=%.2f EUR)", game.title, game.steam_app_id, current_price)
    return True
