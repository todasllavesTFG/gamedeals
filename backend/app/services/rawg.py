import asyncio
import logging

import httpx
from sqlalchemy.orm import Session

from app.config import RAWG_API_KEY
from app.models.games import Game

logger = logging.getLogger(__name__)

RAWG_BASE = "https://api.rawg.io/api"


async def search_game(title: str) -> dict | None:
    params = {"search": title, "key": RAWG_API_KEY, "page_size": 1}
    url = f"{RAWG_BASE}/games"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            logger.info("RAWG search '%s' -> %s", title, response.status_code)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if not results:
                return None
            r = results[0]
            return {
                "id": r["id"],
                "name": r.get("name"),
                "background_image": r.get("background_image"),
                "description_raw": r.get("description_raw", ""),
                "genres": [g["name"] for g in r.get("genres", [])],
                "metacritic": r.get("metacritic"),
                "released": r.get("released"),
            }
    except Exception:
        logger.exception("Error en RAWG search para '%s'", title)
        return None
    finally:
        await asyncio.sleep(0.25)


async def get_game_details(rawg_id: int) -> dict | None:
    url = f"{RAWG_BASE}/games/{rawg_id}"
    params = {"key": RAWG_API_KEY}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            logger.info("RAWG details id=%s -> %s", rawg_id, response.status_code)
            response.raise_for_status()
            r = response.json()
            return {
                "id": r["id"],
                "name": r.get("name"),
                "background_image": r.get("background_image"),
                "description_raw": r.get("description_raw", ""),
                "genres": [g["name"] for g in r.get("genres", [])],
                "metacritic": r.get("metacritic"),
                "released": r.get("released"),
                "platforms": [p["platform"]["name"] for p in r.get("platforms", []) if p.get("platform")],
            }
    except Exception:
        logger.exception("Error en RAWG details para id=%s", rawg_id)
        return None
    finally:
        await asyncio.sleep(0.25)


async def enrich_game_in_db(db: Session, game_id: int) -> bool:
    game = db.query(Game).filter_by(id=game_id).first()
    if not game:
        return False

    result = await search_game(game.title)
    if not result:
        return False

    if result.get("background_image"):
        game.image_url = result["background_image"]
    if result.get("description_raw"):
        game.description = result["description_raw"]
    if result.get("genres"):
        game.genre = result["genres"][0]
    if result.get("metacritic"):
        game.metacritic_score = result["metacritic"]
    game.rawg_id = str(result["id"])

    db.commit()
    logger.info("Juego '%s' enriquecido con RAWG (rawg_id=%s)", game.title, game.rawg_id)
    return True
