import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, contains_eager

from app.database import get_db
from app.models.games import Game
from app.models.prices import Price
from app.models.stores import Store
from app.services.cheapshark import fetch_deals_from_api, save_deals_to_db
from app.services.images import game_image_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deals", tags=["deals"])


# Helper reutilizable para serializar un Price con sus relaciones cargadas
def _serialize_price(p: Price) -> dict:
    return {
        "id": p.id,
        "game": {
            "id": p.game.id,
            "title": p.game.title,
            "slug": p.game.slug,
            "image_url": game_image_url(p.game.image_url, p.game.steam_app_id),
            "metacritic_score": p.game.metacritic_score,
            "platform": p.game.platform,
        },
        "store": {
            "id": p.store.id,
            "name": p.store.name,
        },
        "original_price": p.original_price,
        "current_price": p.current_price,
        "discount_percent": p.discount_percent,
        "deal_url": p.deal_url,
        "last_updated": p.last_updated.isoformat() if p.last_updated else None,
    }


@router.get("")
def get_deals(
    page: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("discount", enum=["discount", "price", "title"]),
    # ── Filtros avanzados (Día 20) ──────────────────────────────────────
    store_id: Optional[int] = Query(None, description="Filtrar por ID de tienda"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo en euros"),
    min_discount: Optional[int] = Query(None, ge=0, le=100, description="Descuento mínimo en %"),
    platform: Optional[str] = Query(None, description="Plataforma (coincidencia parcial)"),
    # ───────────────────────────────────────────────────────────────────
    db: Session = Depends(get_db),
):
    """
    Devuelve deals con soporte de paginación, ordenación y filtros avanzados.

    Filtros opcionales:
    - store_id: solo deals de esta tienda
    - max_price: precio actual <= max_price
    - min_discount: descuento_percent >= min_discount
    - platform: game.platform contiene este texto (case-insensitive)
    """
    # Siempre hacemos JOIN explícito para poder filtrar/ordenar por Game y Store
    query = (
        db.query(Price)
        .join(Price.game)
        .join(Price.store)
        .options(
            contains_eager(Price.game),
            contains_eager(Price.store),
        )
    )

    # ── Aplicar filtros ──────────────────────────────────────────────
    if store_id is not None:
        query = query.filter(Price.store_id == store_id)

    if max_price is not None:
        query = query.filter(Price.current_price <= max_price)

    if min_discount is not None:
        query = query.filter(Price.discount_percent >= min_discount)

    if platform:
        query = query.filter(Game.platform.ilike(f"%{platform}%"))

    # ── Ordenación ───────────────────────────────────────────────────
    if sort_by == "discount":
        query = query.order_by(Price.discount_percent.desc())
    elif sort_by == "price":
        query = query.order_by(Price.current_price.asc())
    elif sort_by == "title":
        query = query.order_by(Game.title.asc())

    prices = query.offset(page * limit).limit(limit).all()

    return [_serialize_price(p) for p in prices]


@router.get("/stores")
def get_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).order_by(Store.name).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "url": s.url,
            "is_scraper": s.is_scraper,
        }
        for s in stores
    ]


@router.post("/refresh")
async def refresh_deals(
    page_size: int = Query(20, ge=1, le=60),
    db: Session = Depends(get_db),
):
    try:
        raw_deals = await fetch_deals_from_api(page_size=page_size)
    except Exception as e:
        logger.exception("Error conectando con CheapShark API")
        raise HTTPException(status_code=502, detail=f"Error al conectar con CheapShark: {e}")

    result = save_deals_to_db(db, raw_deals)
    return {
        "message": "Sincronización completada",
        **result,
    }


@router.get("/search")
def search_deals(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    prices = (
        db.query(Price)
        .join(Price.game)
        .join(Price.store)
        .options(
            contains_eager(Price.game),
            contains_eager(Price.store),
        )
        .filter(Game.title.ilike(f"%{q}%"))
        .order_by(Price.discount_percent.desc())
        .limit(50)
        .all()
    )

    return [_serialize_price(p) for p in prices]
