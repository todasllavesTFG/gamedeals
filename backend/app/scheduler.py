import logging
from datetime import UTC, datetime, timedelta

import httpx
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import SessionLocal
from app.models.alerts import Alert
from app.models.games import Game
from app.models.price_history import PriceHistory
from app.models.prices import Price
from app.models.stores import Store
from app.models.users import User

logger = logging.getLogger(__name__)

CHEAPSHARK_API = "https://www.cheapshark.com/api/1.0"

CHEAPSHARK_STORE_MAP = {
    "1": "Steam",
    "7": "GOG",
    "15": "Fanatical",
    "11": "Humble Bundle",
}

scheduler = AsyncIOScheduler(
    executors={"default": AsyncIOExecutor()},
    job_defaults={"coalesce": True, "max_instances": 1},
)


def _upsert_price_and_history(
    db,
    game_id: int,
    store_id: int,
    original_price: float,
    current_price: float,
    discount: int,
    deal_url: str,
    now: datetime,
) -> None:
    existing = db.query(Price).filter_by(game_id=game_id, store_id=store_id).first()
    if existing:
        existing.original_price = original_price
        existing.current_price = current_price
        existing.discount_percent = discount
        existing.deal_url = deal_url
        existing.last_updated = now
    else:
        db.add(Price(
            game_id=game_id,
            store_id=store_id,
            original_price=original_price,
            current_price=current_price,
            discount_percent=discount,
            deal_url=deal_url,
            last_updated=now,
        ))

    db.add(PriceHistory(
        game_id=game_id,
        store_id=store_id,
        price=current_price,
        recorded_at=now,
    ))


def _get_or_create_store(db, name: str) -> Store:
    store = db.query(Store).filter_by(name=name).first()
    if not store:
        store = Store(name=name, is_scraper=False)
        db.add(store)
        db.flush()
    return store


async def update_cheapshark_prices():
    logger.info("=== Job CheapShark: iniciando actualización de precios ===")
    db = SessionLocal()
    games_processed = 0
    prices_updated = 0

    try:
        games = db.query(Game).filter(Game.title != None).all()  # noqa: E711
        logger.info("CheapShark job: %d juegos en BD para procesar", len(games))

        # Extraer datos necesarios antes del loop async para no mezclar sesiones
        game_data = [(g.id, g.title) for g in games]

        async with httpx.AsyncClient(timeout=15.0, headers={"User-Agent": "GameDeals/1.0"}) as client:
            for game_id, game_title in game_data:
                try:
                    response = await client.get(
                        f"{CHEAPSHARK_API}/deals",
                        params={
                            "title": game_title,
                            "pageSize": 10,
                            "storeID": ",".join(CHEAPSHARK_STORE_MAP.keys()),
                        },
                    )
                    if response.status_code != 200:
                        logger.warning("CheapShark '%s' -> HTTP %d", game_title, response.status_code)
                        continue

                    deals = response.json()
                    if not deals:
                        logger.info("CheapShark: sin resultados para '%s'", game_title)
                        continue

                    logger.debug("CheapShark '%s' -> %d deals", game_title, len(deals))
                    now = datetime.now(UTC)

                    # Agrupar por tienda y quedarse con el deal más barato de cada una
                    best_by_store: dict[str, dict] = {}
                    for deal in deals:
                        cs_store_id = str(deal.get("storeID", ""))
                        store_name = CHEAPSHARK_STORE_MAP.get(cs_store_id)
                        if not store_name:
                            continue
                        sale_price = float(deal.get("salePrice", 0))
                        if store_name not in best_by_store or sale_price < float(best_by_store[store_name].get("salePrice", 0)):
                            best_by_store[store_name] = deal

                    for store_name, deal in best_by_store.items():
                        original_price = float(deal.get("normalPrice", 0))
                        current_price = float(deal.get("salePrice", 0))
                        if original_price <= 0:
                            continue

                        discount = round(((original_price - current_price) / original_price) * 100)
                        deal_url = f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID', '')}"

                        store = _get_or_create_store(db, store_name)
                        _upsert_price_and_history(db, game_id, store.id, original_price, current_price, discount, deal_url, now)
                        db.flush()
                        prices_updated += 1

                    games_processed += 1

                except Exception:
                    logger.exception("CheapShark: error procesando juego '%s'", game_title)
                    db.rollback()
                    continue

        db.commit()
        logger.info("=== Job CheapShark completado: %d juegos procesados, %d precios actualizados ===", games_processed, prices_updated)

    except Exception:
        logger.exception("CheapShark job: error general")
        db.rollback()
    finally:
        db.close()


async def update_steam_prices():
    logger.info("=== Job Steam: iniciando actualización de precios ===")
    db = SessionLocal()
    games_processed = 0
    prices_updated = 0

    try:
        games = db.query(Game).filter(Game.steam_app_id != None).all()  # noqa: E711
        logger.info("Steam job: %d juegos con steam_app_id para procesar", len(games))

        game_data = [(g.id, g.title, g.steam_app_id) for g in games]

        async with httpx.AsyncClient(timeout=15.0) as client:
            for game_id, game_title, steam_app_id in game_data:
                try:
                    response = await client.get(
                        "https://store.steampowered.com/api/appdetails",
                        params={"appids": steam_app_id, "cc": "es", "l": "es"},
                    )
                    if response.status_code == 429:
                        logger.warning("Steam rate limit para app_id=%s, saltando", steam_app_id)
                        continue
                    if response.status_code != 200:
                        logger.warning("Steam '%s' (app_id=%s) -> HTTP %d", game_title, steam_app_id, response.status_code)
                        continue

                    data = response.json()
                    app_data = data.get(str(steam_app_id), {})
                    if not app_data.get("success"):
                        continue

                    price_overview = app_data.get("data", {}).get("price_overview")
                    if not price_overview:
                        logger.debug("Steam: '%s' sin precio (F2P o bundle)", game_title)
                        continue

                    original_price = price_overview["initial"] / 100
                    current_price = price_overview["final"] / 100
                    discount = price_overview.get("discount_percent", 0)
                    deal_url = f"https://store.steampowered.com/app/{steam_app_id}"
                    now = datetime.now(UTC)

                    steam_store = _get_or_create_store(db, "Steam")
                    _upsert_price_and_history(db, game_id, steam_store.id, original_price, current_price, discount, deal_url, now)
                    db.flush()
                    prices_updated += 1
                    games_processed += 1

                except Exception:
                    logger.exception("Steam: error procesando juego '%s' (app_id=%s)", game_title, steam_app_id)
                    db.rollback()
                    continue

        db.commit()
        logger.info("=== Job Steam completado: %d juegos procesados, %d precios actualizados ===", games_processed, prices_updated)

    except Exception:
        logger.exception("Steam job: error general")
        db.rollback()
    finally:
        db.close()


async def update_fanatical_prices():
    from app.services.fanatical import scrape_fanatical_deals, save_fanatical_deals_to_db
    logger.info("=== Job Fanatical: iniciando scraping de ofertas ===")
    db = SessionLocal()
    try:
        deals = await scrape_fanatical_deals()
        logger.info("Fanatical job: %d deals scrapeados", len(deals))
        result = save_fanatical_deals_to_db(db, deals)
        logger.info("=== Job Fanatical completado: %s ===", result)
    except Exception:
        logger.exception("Fanatical job: error general")
        db.rollback()
    finally:
        db.close()


async def update_humble_bundles():
    from app.services.humble import scrape_humble_bundles, save_humble_bundles_to_db
    logger.info("=== Job Humble Bundle: iniciando scraping de bundles ===")
    db = SessionLocal()
    try:
        bundles = await scrape_humble_bundles()
        logger.info("Humble Bundle job: %d bundles scrapeados", len(bundles))
        result = await save_humble_bundles_to_db(db, bundles)
        logger.info("=== Job Humble Bundle completado: %s ===", result)
    except Exception:
        logger.exception("Humble Bundle job: error general")
        db.rollback()
    finally:
        db.close()


async def check_price_alerts():
    """
    Job que comprueba alertas activas y envía emails cuando el precio
    actual está por debajo del precio objetivo configurado por el usuario.
    Se ejecuta cada 30 minutos.
    """
    from app.services.email import send_price_alert_email

    logger.info("=== Job Alertas: comprobando alertas de precio activas ===")
    db = SessionLocal()
    alerts_triggered = 0

    try:
        # Cargar todas las alertas activas y no disparadas con sus relaciones
        active_alerts = (
            db.query(Alert)
            .join(Alert.user)
            .join(Alert.game)
            .filter(
                Alert.is_active == True,   # noqa: E712
                Alert.is_triggered == False,  # noqa: E712
            )
            .all()
        )

        logger.info("Job Alertas: %d alertas activas encontradas", len(active_alerts))

        # Pre-cargar usuarios y juegos para evitar lazy loading en el loop
        from sqlalchemy.orm import joinedload
        alert_ids = [a.id for a in active_alerts]
        if not alert_ids:
            return

        active_alerts = (
            db.query(Alert)
            .options(
                joinedload(Alert.user),
                joinedload(Alert.game),
            )
            .filter(Alert.id.in_(alert_ids))
            .all()
        )

        for alert in active_alerts:
            # Obtener el mejor precio actual para este juego
            best_price_row = (
                db.query(Price)
                .join(Price.store)
                .filter(Price.game_id == alert.game_id)
                .order_by(Price.current_price.asc())
                .first()
            )

            if best_price_row is None:
                logger.debug(
                    "Alerta #%d: juego '%s' sin precios en BD, saltando",
                    alert.id,
                    alert.game.title if alert.game else "desconocido",
                )
                continue

            game_title = alert.game.title if alert.game else "Juego desconocido"
            current_price = best_price_row.current_price

            logger.debug(
                "Alerta #%d | juego='%s' | precio actual=%.2f€ | objetivo=%.2f€",
                alert.id,
                game_title,
                current_price,
                alert.target_price,
            )

            if current_price <= alert.target_price:
                logger.info(
                    "¡Alerta #%d disparada! '%s' — %.2f€ <= %.2f€ (objetivo) en %s",
                    alert.id,
                    game_title,
                    current_price,
                    alert.target_price,
                    best_price_row.store.name,
                )

                # Marcar como disparada ANTES de enviar el email
                alert.is_triggered = True
                alert.triggered_at = datetime.now(UTC)
                alert.is_active = False
                db.flush()

                # Enviar email (síncrono — smtplib)
                send_price_alert_email(
                    to_email=alert.user.email,
                    username=alert.user.username,
                    game_title=game_title,
                    target_price=alert.target_price,
                    current_price=current_price,
                    store_name=best_price_row.store.name,
                    deal_url=best_price_row.deal_url or "",
                )
                alerts_triggered += 1

        db.commit()
        logger.info(
            "=== Job Alertas completado: %d/%d alertas disparadas ===",
            alerts_triggered,
            len(active_alerts),
        )

    except Exception:
        logger.exception("Job Alertas: error general")
        db.rollback()
    finally:
        db.close()


def register_jobs():
    now = datetime.now()
    scheduler.add_job(
        update_cheapshark_prices,
        trigger="interval",
        hours=1,
        id="cheapshark_prices",
        name="Actualización precios CheapShark",
        next_run_time=now,
        replace_existing=True,
    )
    # Steam arranca 60s después de CheapShark para evitar contención en SQLite
    scheduler.add_job(
        update_steam_prices,
        trigger="interval",
        hours=2,
        id="steam_prices",
        name="Actualización precios Steam",
        next_run_time=now + timedelta(seconds=60),
        replace_existing=True,
    )
    scheduler.add_job(
        update_fanatical_prices,
        trigger="interval",
        hours=6,
        id="fanatical_prices",
        name="Scraping ofertas Fanatical",
        next_run_time=now + timedelta(seconds=120),
        replace_existing=True,
    )
    scheduler.add_job(
        update_humble_bundles,
        trigger="interval",
        hours=6,
        id="humble_bundles",
        name="Scraping bundles Humble Bundle",
        next_run_time=now + timedelta(seconds=180),
        replace_existing=True,
    )
    scheduler.add_job(
        check_price_alerts,
        trigger="interval",
        minutes=30,
        id="check_price_alerts",
        name="Comprobación alertas de precio",
        next_run_time=now + timedelta(seconds=30),
        replace_existing=True,
    )
    logger.info(
        "Jobs registrados: cheapshark_prices (1h), steam_prices (2h), "
        "fanatical_prices (6h), humble_bundles (6h), check_price_alerts (30min)"
    )
