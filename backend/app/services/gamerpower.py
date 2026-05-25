import logging
import re

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.gamerpower.com/api/giveaways"
_VALID_PLATFORMS = {"pc", "steam", "epic-games-store"}


def _parse_worth(worth: str) -> float:
    if not worth or worth == "N/A":
        return 0.0
    match = re.search(r"[\d.]+", worth)
    return float(match.group()) if match else 0.0


def get_free_games(platform: str = "all") -> list[dict]:
    # GamerPower no acepta platform=all; hay que omitir el parámetro para obtener todos
    if platform in _VALID_PLATFORMS:
        url = f"{_BASE_URL}?platform={platform}&type=game"
    else:
        url = f"{_BASE_URL}?type=game"
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("GamerPower: error al obtener giveaways: %s", exc)
        return []

    if not isinstance(data, list):
        logger.warning("GamerPower: formato de respuesta inesperado")
        return []

    games: list[dict] = []
    for item in data:
        try:
            if item.get("status") != "Active":
                continue

            end_date = item.get("end_date")
            if end_date == "N/A":
                end_date = None

            games.append(
                {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "image_url": item.get("image", ""),
                    "original_price": _parse_worth(item.get("worth", "N/A")),
                    "current_price": 0.0,
                    "store": item.get("platforms", ""),
                    "deal_url": item.get("open_giveaway_url", ""),
                    "end_date": end_date,
                    "source": "gamerpower",
                }
            )
        except Exception as exc:
            logger.debug("GamerPower: error procesando giveaway: %s", exc)
            continue

    logger.info("GamerPower: %d juego(s) activo(s) encontrado(s)", len(games))
    return games
