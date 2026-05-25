import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query

from app.services import epic, gamerpower

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Free Games"])

# ── Caché en memoria ────────────────────────────────────────────────────────
CACHE_TTL_SECONDS = 3600

_cache_all: dict[str, Any] = {"data": None, "timestamp": None}
_cache_epic: dict[str, Any] = {"data": None, "timestamp": None}
_cache_gamerpower: dict[str, Any] = {"data": None, "timestamp": None}


def _cache_valid(cache: dict) -> bool:
    if cache["data"] is None or cache["timestamp"] is None:
        return False
    age = (datetime.now(timezone.utc) - cache["timestamp"]).total_seconds()
    return age < CACHE_TTL_SECONDS


def _build_response(games: list[dict]) -> dict:
    # Eliminar duplicados por título: Epic tiene prioridad sobre GamerPower
    seen: dict[str, dict] = {}
    for g in games:
        title_key = g["title"].lower().strip()
        if title_key not in seen:
            seen[title_key] = g
        elif g["source"] == "epic":
            seen[title_key] = g

    unique = sorted(seen.values(), key=lambda g: g["original_price"], reverse=True)
    return {
        "total": len(unique),
        "games": unique,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


# ── Helpers async (los servicios usan httpx síncrono) ───────────────────────

async def _fetch_epic() -> list[dict]:
    return await asyncio.to_thread(epic.get_free_games)


async def _fetch_gamerpower(platform: str = "all") -> list[dict]:
    return await asyncio.to_thread(gamerpower.get_free_games, platform)


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/free-games")
async def get_free_games_endpoint(
    source: str = Query(default="all", description="'epic', 'gamerpower' o 'all'"),
    platform: str = Query(default="all", description="Solo GamerPower: 'pc', 'steam', 'all'"),
):
    """
    Devuelve juegos gratuitos de Epic Games Store y/o GamerPower combinados.
    Resultados cacheados 1 hora en memoria.
    """
    if source == "epic":
        if _cache_valid(_cache_epic):
            logger.info("GET /free-games?source=epic → caché válida")
            return _cache_epic["data"]
        games = await _fetch_epic()
        result = _build_response(games)
        _cache_epic["data"] = result
        _cache_epic["timestamp"] = datetime.now(timezone.utc)
        return result

    if source == "gamerpower":
        if _cache_valid(_cache_gamerpower):
            logger.info("GET /free-games?source=gamerpower → caché válida")
            return _cache_gamerpower["data"]
        games = await _fetch_gamerpower(platform)
        result = _build_response(games)
        _cache_gamerpower["data"] = result
        _cache_gamerpower["timestamp"] = datetime.now(timezone.utc)
        return result

    # source == "all"
    if _cache_valid(_cache_all):
        logger.info("GET /free-games → caché válida")
        return _cache_all["data"]

    epic_games, gp_games = await asyncio.gather(
        _fetch_epic(),
        _fetch_gamerpower(platform),
    )
    result = _build_response(epic_games + gp_games)
    _cache_all["data"] = result
    _cache_all["timestamp"] = datetime.now(timezone.utc)
    return result


@router.get("/free-games/epic")
async def get_free_games_epic():
    """Shortcut: devuelve solo los juegos gratuitos de Epic Games Store."""
    if _cache_valid(_cache_epic):
        logger.info("GET /free-games/epic → caché válida")
        return _cache_epic["data"]
    games = await _fetch_epic()
    result = _build_response(games)
    _cache_epic["data"] = result
    _cache_epic["timestamp"] = datetime.now(timezone.utc)
    return result


@router.get("/free-games/gamerpower")
async def get_free_games_gamerpower():
    """Shortcut: devuelve solo los juegos gratuitos de GamerPower."""
    if _cache_valid(_cache_gamerpower):
        logger.info("GET /free-games/gamerpower → caché válida")
        return _cache_gamerpower["data"]
    games = await _fetch_gamerpower()
    result = _build_response(games)
    _cache_gamerpower["data"] = result
    _cache_gamerpower["timestamp"] = datetime.now(timezone.utc)
    return result
