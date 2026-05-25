import logging
import re
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.games import Game
from app.models.prices import Price
from app.models.price_history import PriceHistory
from app.models.stores import Store

logger = logging.getLogger(__name__)

HUMBLE_URL = "https://www.humblebundle.com/bundles"


def _slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug


def _get_or_create_store(db: Session) -> Store:
    store = db.query(Store).filter_by(name="Humble Bundle").first()
    if not store:
        store = Store(name="Humble Bundle", url="https://www.humblebundle.com", is_scraper=True)
        db.add(store)
        db.flush()
    return store


async def scrape_humble_bundles() -> list[dict]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error(
            "Playwright no instalado. Ejecuta: pip install playwright && python -m playwright install chromium"
        )
        return []

    bundles = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(HUMBLE_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector(
                'a[href*="/games/"], [class*="bundle"]', timeout=15000
            )

            raw_bundles = await page.evaluate("""
                () => {
                    const results = [];
                    const selectors = [
                        'a[href*="/games/"]',
                        '[class*="bundle-card"]',
                        '[class*="bundle-grid"] > a',
                        '[class*="mosaic"] a',
                        '[class*="tile"] a',
                    ];
                    const seen = new Set();
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(card => {
                            const key = card.href || card.innerText;
                            if (seen.has(key)) return;
                            seen.add(key);
                            const titleEl = card.querySelector('h2, h3, [class*="title"], [class*="name"]');
                            const priceEl = card.querySelector('[class*="price"], [class*="cost"], [class*="amount"]');
                            const imgEl = card.querySelector('img');
                            const href = card.tagName === 'A' ? card.href : (card.querySelector('a') || {}).href;
                            if (titleEl) {
                                results.push({
                                    title: titleEl.innerText.trim(),
                                    priceText: priceEl ? priceEl.innerText.trim() : null,
                                    img: imgEl ? (imgEl.src || imgEl.dataset.src) : null,
                                    href: href || null,
                                });
                            }
                        });
                    });
                    return results;
                }
            """)

            for b in raw_bundles:
                if not b.get("title"):
                    continue

                price_text = b.get("priceText") or ""
                price_match = re.search(r"[\d]+[.,][\d]+|[\d]+", price_text.replace(",", "."))
                price = float(price_match.group().replace(",", ".")) if price_match else 0.0

                href = b.get("href") or ""
                if href and not href.startswith("http"):
                    href = f"https://www.humblebundle.com{href}"

                bundles.append({
                    "title": b["title"],
                    "current_price": price,
                    "image_url": b.get("img"),
                    "deal_url": href or HUMBLE_URL,
                })

        except Exception:
            logger.exception("Humble Bundle: error durante scraping")
        finally:
            await browser.close()

    logger.info("Humble Bundle: %d bundles extraídos", len(bundles))
    return bundles


async def save_humble_bundles_to_db(db: Session, bundles: list[dict]) -> dict:
    games_created = 0
    prices_updated = 0
    history_added = 0
    skipped = 0

    store = _get_or_create_store(db)
    now = datetime.now(UTC)

    for bundle in bundles:
        try:
            title = bundle.get("title")
            current_price = float(bundle.get("current_price", 0.0))
            image_url = bundle.get("image_url")
            deal_url = bundle.get("deal_url")

            if not title:
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
                existing_price.original_price = current_price
                existing_price.current_price = current_price
                existing_price.discount_percent = 0
                existing_price.deal_url = deal_url
                existing_price.last_updated = now
            else:
                db.add(Price(
                    game_id=game.id,
                    store_id=store.id,
                    original_price=current_price,
                    current_price=current_price,
                    discount_percent=0,
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
            logger.exception("Humble Bundle: error guardando bundle '%s'", bundle.get("title"))
            skipped += 1
            continue

    db.commit()
    result = {
        "games_created": games_created,
        "prices_updated": prices_updated,
        "history_added": history_added,
        "skipped": skipped,
        "total_processed": len(bundles),
    }
    logger.info("Humble Bundle sync completado: %s", result)
    return result
