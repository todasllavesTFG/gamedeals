from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models.games import Game
from app.models.prices import Price
from app.models.users import User
from app.models.wishlist import Wishlist
from app.routers.auth import get_current_user, get_db
from app.schemas.wishlist import BestPriceInfo, GameInWishlist, WishlistItemOut

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


def _serialize_item(item: Wishlist) -> WishlistItemOut:
    best_price = None
    if item.game.prices:
        cheapest = min(item.game.prices, key=lambda p: p.current_price)
        best_price = BestPriceInfo(
            store_name=cheapest.store.name,
            current_price=cheapest.current_price,
            discount_percent=cheapest.discount_percent,
            deal_url=cheapest.deal_url,
        )
    return WishlistItemOut(
        id=item.id,
        game_id=item.game_id,
        added_at=item.added_at,
        game=GameInWishlist(
            id=item.game.id,
            title=item.game.title,
            slug=item.game.slug,
            image_url=item.game.image_url,
            metacritic_score=item.game.metacritic_score,
        ),
        best_price=best_price,
    )


def _load_with_relations(db: Session, user_id: int, game_id: int | None = None) -> Wishlist | None:
    q = (
        db.query(Wishlist)
        .options(
            joinedload(Wishlist.game)
            .joinedload(Game.prices)
            .joinedload(Price.store)
        )
        .filter(Wishlist.user_id == user_id)
    )
    if game_id is not None:
        q = q.filter(Wishlist.game_id == game_id)
    return q.first()


@router.get("", response_model=list[WishlistItemOut])
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Wishlist)
        .options(
            joinedload(Wishlist.game)
            .joinedload(Game.prices)
            .joinedload(Price.store)
        )
        .filter(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.added_at.desc())
        .all()
    )
    return [_serialize_item(i) for i in items]


@router.post("/{game_id}", response_model=WishlistItemOut, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    existing = _load_with_relations(db, current_user.id, game_id)
    if existing:
        return _serialize_item(existing)

    try:
        item = Wishlist(user_id=current_user.id, game_id=game_id)
        db.add(item)
        db.commit()

        loaded = (
            db.query(Wishlist)
            .options(
                joinedload(Wishlist.game)
                .joinedload(Game.prices)
                .joinedload(Price.store)
            )
            .filter(Wishlist.id == item.id)
            .first()
        )
        return _serialize_item(loaded)

    except IntegrityError:
        db.rollback()
        existing = _load_with_relations(db, current_user.id, game_id)
        if existing:
            return _serialize_item(existing)
        raise HTTPException(status_code=400, detail="Error al añadir a wishlist")


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(Wishlist)
        .filter(Wishlist.user_id == current_user.id, Wishlist.game_id == game_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="El juego no está en tu wishlist")
    db.delete(item)
    db.commit()
