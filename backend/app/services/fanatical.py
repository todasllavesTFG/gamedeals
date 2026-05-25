import logging
import re
from datetime import UTC, datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.games import Game
from app.models.prices import Price
from app.models.price_history import PriceHistory
from app.models.stores import Store

logger = logging.getLogger(__name__)

FANATICAL_URL = "https://www.fanatical.com/es/on-sale"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com",
}


def _parse_price(text: str) -> float:
    if not text:
        return 0.0
    cleaned = text.replace("€", "").replace("\xa0", "").replace(" ", "").replace(" ", "").strip()
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug


def _get_or_create_store(db: Session) -> Store:
    store = db.query(Store).filter_by(name="Fanatical").first()
    if not store:
        store = Store(name="Fanatical", url="https://www.fanatical.com", is_scraper=True)
        db.add(store)
        db.flush()
    return store


async def scrape_fanatical_deals(limit: int = 60) -> list[dict]:
    async with httpx.AsyncClient(timeout=20, headers=HEADERS, follow_redirects=True) as client:
        try:
            response = await client.get(FANATICAL_URL)
        except Exception:
            logger.exception("Fanatical: error de conexión")
            return []

    if response.status_code != 200:
        logger.warning("Fanatical: HTTP %d al obtener %s", response.status_code, FANATICAL_URL)
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Intentar múltiples selectores para robustez
    cards = soup.select('[data-testid="product-card"]')
    if not cards:
        cards = soup.select('a[href*="/es/game/"]')
    if not cards:
        cards = soup.find_all("article")
    if not cards:
        cards = soup.select('[class*="product-card"]')
    if not cards:
        cards = soup.select('[class*="product"]')

    logger.info("Fanatical: encontradas %d cards con selector", len(cards))
    deals = []

    for card in cards[:limit]:
        try:
            # Extraer título
            title_el = (
                card.select_one('[class*="title"]')
                or card.select_one('[class*="name"]')
                or card.select_one("h3")
                or card.select_one("h2")
            )
            title = title_el.get_text(strip=True) if title_el else None
            if not title:
                continue

            # Extraer precios
            current_price = 0.0
            original_price = 0.0

            price_els = card.select('[class*="price"]')
            prices_found = []
            for p_el in price_els:
                val = _parse_price(p_el.get_text(strip=True))
                if val > 0:
                    cls = " ".join(p_el.get("class", []))
                    prices_found.append((val, cls))

            if not prices_found:
                continue

            prices_found.sort(key=lambda x: x[0])
            current_price = prices_found[0][0]
            original_price = prices_found[-1][0] if len(prices_found) > 1 else current_price

            if current_price <= 0:
                continue

            discount_percent = (
                round(((original_price - current_price) / original_price) * 100)
                if original_price > current_price
                else 0
            )

            # Extraer imagen
            img_el = card.select_one("img")
            image_url = None
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy-src")

            # Extraer URL de la oferta
            link_el = card if card.name == "a" else card.select_one("a[href]")
            deal_url = None
            if link_el:
                href = link_el.get("href", "")
                deal_url = href if href.startswith("http") else f"https://www.fanatical.com{href}"

            deals.append({
                "title": title,
                "current_price": current_price,
                "original_price": original_price,
                "discount_percent": discount_percent,
                "image_url": image_url,
                "deal_url": deal_url,
            })

        except Exception:
            logger.exception("Fanatical: error parseando card")
            continue

    logger.info("Fanatical: %d deals válidos extraídos", len(deals))
    return deals


def save_fanatical_deals_to_db(db: Session, deals: list[dict]) -> dict:
    games_created = 0
    prices_updated = 0
    history_added = 0
    skipped = 0

    store = _get_or_create_store(db)
    now = datetime.now(UTC)

    for deal in deals:
        try:
            title = deal.get("title")
            current_price = float(deal.get("current_price", 0.0))
            original_price = float(deal.get("original_price", current_price))
            discount_percent = int(deal.get("discount_percent", 0))
            image_url = deal.get("image_url")
            deal_url = deal.get("deal_url")

            if not title or current_price <= 0:
                skipped += 1
                continue

            slug = _slugify(title)
            game = db.query(Game).filter_by(slug=slug).first()
            if not game:
                game = Game(title=title, slug=slug, image_url=image_url, platform="PC")
                db.add(game)
                db.flush()
                games_created += 1

            existing_price = db.query(Price).filter_by(game_id=game.id, store_id=store.id).first()
            if existing_price:
                existing_price.original_price = original_price
                existing_price.current_price = current_price
                existing_price.discount_percent = discount_percent
                existing_price.deal_url = deal_url
                existing_price.last_updated = now
            else:
                db.add(Price(
                    game_id=game.id,
                    store_id=store.id,
                    original_price=original_price,
                    current_price=current_price,
                    discount_percent=discount_percent,
                    deal_url=deal_url,
                    last_updated=now,
                ))

            db.add(PriceHistory(
                game_id=game.id,
                store_id=store.id,
                price=current_price,
                recorded_at=now,
            ))
            history_added += 1
            prices_updated += 1

        except Exception:
            logger.exception("Fanatical: error guardando deal '%s'", deal.get("title"))
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
    logger.info("Fanatical sync completado: %s", result)
    return result
