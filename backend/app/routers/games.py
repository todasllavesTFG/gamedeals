import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.games import Game
from app.models.price_history import PriceHistory
from app.models.stores import Store
from app.services.aggregator import get_unified_game
from app.services.rawg import enrich_game_in_db
from app.services.steam import enrich_game_with_steam

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/{game_id}")
def get_game(game_id: int, db: Session = Depends(get_db)):
    result = get_unified_game(db, game_id)
    if not result:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return result


@router.get("/{game_id}/history")
def get_game_history(
    game_id: int,
    store_id: int | None = Query(default=None),
    days: int = Query(default=30),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter_by(id=game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    since = datetime.now(UTC) - timedelta(days=days)

    query = db.query(PriceHistory).filter(
        PriceHistory.game_id == game_id,
        PriceHistory.recorded_at >= since,
    )
    if store_id is not None:
        query = query.filter(PriceHistory.store_id == store_id)

    records = query.order_by(PriceHistory.recorded_at.asc()).all()

    store_ids = {r.store_id for r in records}
    stores_by_id = {s.id: s.name for s in db.query(Store).filter(Store.id.in_(store_ids)).all()}

    history: dict[str, list] = {}
    for record in records:
        store_name = stores_by_id.get(record.store_id, f"store_{record.store_id}")
        if store_name not in history:
            history[store_name] = []
        history[store_name].append({
            "price": record.price,
            "recorded_at": record.recorded_at.isoformat(),
        })

    all_time_low = None
    if records:
        lowest = min(records, key=lambda r: r.price)
        all_time_low = {
            "price": lowest.price,
            "store": stores_by_id.get(lowest.store_id, f"store_{lowest.store_id}"),
            "recorded_at": lowest.recorded_at.isoformat(),
        }

    return {
        "game_id": game_id,
        "game_title": game.title,
        "days": days,
        "history": history,
        "all_time_low": all_time_low,
    }


@router.get("/{game_id}/enrich")
async def enrich_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(id=game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    rawg_ok = await enrich_game_in_db(db, game_id)
    steam_ok = await enrich_game_with_steam(db, game_id)

    logger.info("Enrich game_id=%d: rawg=%s, steam=%s", game_id, rawg_ok, steam_ok)

    result = get_unified_game(db, game_id)
    return {
        "enriched": {"rawg": rawg_ok, "steam": steam_ok},
        "game": result,
    }


@router.post("/enrich-all")
async def enrich_all_games(db: Session = Depends(get_db)):
    games = db.query(Game).all()
    enriched_count = 0
    errors = []

    for game in games:
        try:
            rawg_ok = await enrich_game_in_db(db, game.id)
            steam_ok = await enrich_game_with_steam(db, game.id)
            if rawg_ok or steam_ok:
                enriched_count += 1
        except Exception:
            logger.exception("Error enriqueciendo juego '%s' (id=%d)", game.title, game.id)
            errors.append(game.title)

    return {
        "total_games": len(games),
        "enriched": enriched_count,
        "errors": errors,
    }
