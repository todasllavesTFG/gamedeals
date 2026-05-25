import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

_EPIC_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    "?locale=es-ES&country=ES&allowCountries=ES"
)


def _parse_price(cents: int) -> float:
    return round(cents / 100, 2)


def _active_offer(promotions: dict) -> dict | None:
    """Devuelve el primer promotional offer activo ahora mismo, o None."""
    now = datetime.now(timezone.utc)
    for group in promotions.get("promotionalOffers", []):
        for offer in group.get("promotionalOffers", []):
            try:
                start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
            except (KeyError, ValueError):
                continue
            if start <= now <= end:
                return offer
    return None


def get_free_games() -> list[dict]:
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(_EPIC_URL)
            resp.raise_for_status()
            data = resp.json()

        elements = (
            data.get("data", {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )
    except Exception as exc:
        logger.warning("Epic Games: error al obtener juegos gratuitos: %s", exc)
        return []

    games: list[dict] = []
    for el in elements:
        try:
            promotions = el.get("promotions") or {}
            offer = _active_offer(promotions)
            if not offer:
                continue

            original_price = _parse_price(
                el.get("price", {}).get("totalPrice", {}).get("originalPrice", 0)
            )
            if original_price == 0.0:
                # Free-to-play permanente — no nos interesa
                continue

            title = el.get("title", "")
            description = el.get("description", "")

            image_url = ""
            for img in el.get("keyImages", []):
                if img.get("type") == "Thumbnail":
                    image_url = img.get("url", "")
                    break

            product_slug = el.get("productSlug") or el.get("urlSlug") or ""
            deal_url = f"https://store.epicgames.com/es-ES/p/{product_slug}"

            end_date = offer.get("endDate", "")

            games.append(
                {
                    "title": title,
                    "description": description,
                    "image_url": image_url,
                    "original_price": original_price,
                    "current_price": 0.0,
                    "store": "Epic Games Store",
                    "deal_url": deal_url,
                    "end_date": end_date,
                    "source": "epic",
                }
            )
        except Exception as exc:
            logger.debug("Epic Games: error procesando elemento: %s", exc)
            continue

    logger.info("Epic Games: %d juego(s) gratuito(s) encontrado(s)", len(games))
    return games
