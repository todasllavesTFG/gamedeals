import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.alerts import Alert
from app.models.games import Game
from app.models.prices import Price
from app.models.users import User
from app.routers.auth import get_current_user
from app.schemas.alerts import AlertCreate, AlertOut, AlertUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _load_with_relations(db: Session, alert_id: int) -> Optional[Alert]:
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.game).joinedload(Game.prices).joinedload(Price.store)
        )
        .filter(Alert.id == alert_id)
        .first()
    )


def _serialize(alert: Alert) -> AlertOut:
    game = alert.game
    current_best_price = None
    best_store_name = None

    if game and game.prices:
        cheapest = min(game.prices, key=lambda p: p.current_price)
        current_best_price = cheapest.current_price
        best_store_name = cheapest.store.name if cheapest.store else None

    return AlertOut(
        id=alert.id,
        game_id=alert.game_id,
        target_price=alert.target_price,
        is_active=alert.is_active,
        is_triggered=alert.is_triggered,
        triggered_at=alert.triggered_at,
        created_at=alert.created_at,
        game_title=game.title if game else None,
        game_image=game.image_url if game else None,
        current_best_price=current_best_price,
        best_store_name=best_store_name,
    )


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.get("", response_model=list[AlertOut])
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve todas las alertas del usuario autenticado, ordenadas por fecha de creación."""
    alerts = (
        db.query(Alert)
        .options(
            joinedload(Alert.game).joinedload(Game.prices).joinedload(Price.store)
        )
        .filter(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
        .all()
    )
    return [_serialize(a) for a in alerts]


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(
    body: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea una nueva alerta de precio. Solo se permite una alerta activa por juego/usuario."""
    game = db.query(Game).filter(Game.id == body.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    existing = (
        db.query(Alert)
        .filter(
            Alert.user_id == current_user.id,
            Alert.game_id == body.game_id,
            Alert.is_active == True,  # noqa: E712
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Ya tienes una alerta activa para este juego",
        )

    alert = Alert(
        user_id=current_user.id,
        game_id=body.game_id,
        target_price=body.target_price,
        is_active=True,
        is_triggered=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    loaded = _load_with_relations(db, alert.id)
    return _serialize(loaded)


@router.patch("/{alert_id}", response_model=AlertOut)
def update_alert(
    alert_id: int,
    body: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza el precio objetivo o el estado activo/pausado de una alerta.
    Al reactivar una alerta disparada (is_active=True), resetea is_triggered a False
    para que el scheduler la vuelva a evaluar.
    """
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    if body.target_price is not None:
        alert.target_price = body.target_price

    if body.is_active is not None:
        alert.is_active = body.is_active
        # Si el usuario reactiva una alerta ya disparada, la resetea
        if body.is_active and alert.is_triggered:
            alert.is_triggered = False
            alert.triggered_at = None

    db.commit()

    loaded = _load_with_relations(db, alert.id)
    return _serialize(loaded)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina permanentemente una alerta del usuario."""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    db.delete(alert)
    db.commit()
