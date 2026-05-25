import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Base, SessionLocal, engine
from app.models import Game, Price, PriceHistory, Store

Base.metadata.create_all(bind=engine)

STORES = [
    {
        "name": "Steam",
        "url": "https://store.steampowered.com",
        "logo_url": None,
        "is_scraper": False,
    },
    {
        "name": "GOG",
        "url": "https://www.gog.com",
        "logo_url": None,
        "is_scraper": False,
    },
    {
        "name": "Fanatical",
        "url": "https://www.fanatical.com",
        "logo_url": None,
        "is_scraper": True,
    },
    {
        "name": "Humble Bundle",
        "url": "https://www.humblebundle.com",
        "logo_url": None,
        "is_scraper": True,
    },
]

GAMES = [
    {
        "title": "Elden Ring",
        "slug": "elden-ring",
        "description": "Juego de rol de acción en un mundo abierto creado por FromSoftware y George R.R. Martin.",
        "image_url": "https://cdn.rawg.io/elden-ring.jpg",
        "genre": "RPG",
        "platform": "PC",
        "metacritic_score": 96,
        "rawg_id": "326243",
        "steam_app_id": "1245620",
        "original_price": 59.99,
    },
    {
        "title": "Cyberpunk 2077",
        "slug": "cyberpunk-2077",
        "description": "RPG de mundo abierto ambientado en Night City, una megalópolis obsesionada con el poder y la modificación corporal.",
        "image_url": "https://cdn.rawg.io/cyberpunk-2077.jpg",
        "genre": "RPG",
        "platform": "PC",
        "metacritic_score": 90,
        "rawg_id": "41494",
        "steam_app_id": "1091500",
        "original_price": 59.99,
    },
    {
        "title": "Hollow Knight",
        "slug": "hollow-knight",
        "description": "Aventura de acción clásica en 2D ambientada en un vasto mundo interconectado de insectos.",
        "image_url": "https://cdn.rawg.io/hollow-knight.jpg",
        "genre": "Plataformas",
        "platform": "PC",
        "metacritic_score": 90,
        "rawg_id": "9767",
        "steam_app_id": "367520",
        "original_price": 14.99,
    },
    {
        "title": "Hades",
        "slug": "hades",
        "description": "Roguelite de Supergiant Games donde luchas para escapar del Inframundo griego.",
        "image_url": "https://cdn.rawg.io/hades.jpg",
        "genre": "Roguelite",
        "platform": "PC",
        "metacritic_score": 93,
        "rawg_id": "274755",
        "steam_app_id": "1145360",
        "original_price": 24.99,
    },
    {
        "title": "Red Dead Redemption 2",
        "slug": "red-dead-redemption-2",
        "description": "Épica historia del forajido Arthur Morgan y la banda Van der Linde en el ocaso del Salvaje Oeste.",
        "image_url": "https://cdn.rawg.io/rdr2.jpg",
        "genre": "Acción",
        "platform": "Multi",
        "metacritic_score": 97,
        "rawg_id": "28",
        "steam_app_id": "1174180",
        "original_price": 59.99,
    },
    {
        "title": "The Witcher 3",
        "slug": "the-witcher-3",
        "description": "RPG de mundo abierto donde juegas como Geralt de Rivia, cazador de monstruos profesional.",
        "image_url": "https://cdn.rawg.io/witcher3.jpg",
        "genre": "RPG",
        "platform": "PC",
        "metacritic_score": 92,
        "rawg_id": "3328",
        "steam_app_id": "292030",
        "original_price": 39.99,
    },
    {
        "title": "Stardew Valley",
        "slug": "stardew-valley",
        "description": "Simulador de granja con exploración de cuevas, pesca y relaciones con los vecinos del pueblo.",
        "image_url": "https://cdn.rawg.io/stardew-valley.jpg",
        "genre": "Simulación",
        "platform": "Multi",
        "metacritic_score": 89,
        "rawg_id": "34572",
        "steam_app_id": "413150",
        "original_price": 13.99,
    },
    {
        "title": "Celeste",
        "slug": "celeste",
        "description": "Plataformas de precisión que narra la historia de Madeline escalando la montaña Celeste.",
        "image_url": "https://cdn.rawg.io/celeste.jpg",
        "genre": "Plataformas",
        "platform": "PC",
        "metacritic_score": 94,
        "rawg_id": "68540",
        "steam_app_id": "504230",
        "original_price": 19.99,
    },
    {
        "title": "Deep Rock Galactic",
        "slug": "deep-rock-galactic",
        "description": "Shooter cooperativo donde enanos espaciales minan en cuevas alienígenas generadas proceduralmente.",
        "image_url": "https://cdn.rawg.io/deep-rock-galactic.jpg",
        "genre": "Cooperativo",
        "platform": "PC",
        "metacritic_score": 85,
        "rawg_id": "58812",
        "steam_app_id": "548430",
        "original_price": 29.99,
    },
    {
        "title": "Disco Elysium",
        "slug": "disco-elysium",
        "description": "RPG narrativo revolucionario donde eres un detective con amnesia en una ciudad al borde del colapso.",
        "image_url": "https://cdn.rawg.io/disco-elysium.jpg",
        "genre": "RPG",
        "platform": "PC",
        "metacritic_score": 97,
        "rawg_id": "108329",
        "steam_app_id": "632470",
        "original_price": 39.99,
    },
]

STORE_ASSIGNMENTS = {
    "elden-ring": ["Steam", "Fanatical", "Humble Bundle"],
    "cyberpunk-2077": ["Steam", "GOG", "Humble Bundle"],
    "hollow-knight": ["Steam", "GOG", "Humble Bundle"],
    "hades": ["Steam", "GOG"],
    "red-dead-redemption-2": ["Steam", "Fanatical"],
    "the-witcher-3": ["Steam", "GOG", "Fanatical"],
    "stardew-valley": ["Steam", "GOG", "Humble Bundle"],
    "celeste": ["Steam", "GOG"],
    "deep-rock-galactic": ["Steam", "Fanatical", "Humble Bundle"],
    "disco-elysium": ["Steam", "GOG", "Fanatical"],
}


def seed():
    random.seed(42)
    db = SessionLocal()

    stores_created = 0
    games_created = 0
    prices_created = 0
    history_created = 0

    store_map = {}
    for store_data in STORES:
        existing = db.query(Store).filter_by(name=store_data["name"]).first()
        if existing:
            store_map[existing.name] = existing
        else:
            store = Store(**store_data)
            db.add(store)
            db.flush()
            store_map[store.name] = store
            stores_created += 1

    game_map = {}
    for game_data in GAMES:
        original_price = game_data.pop("original_price")
        existing = db.query(Game).filter_by(slug=game_data["slug"]).first()
        if existing:
            game_map[existing.slug] = (existing, original_price)
        else:
            game = Game(**game_data)
            db.add(game)
            db.flush()
            game_map[game.slug] = (game, original_price)
            games_created += 1

    now = datetime.now(UTC)

    for slug, store_names in STORE_ASSIGNMENTS.items():
        game, original_price = game_map[slug]
        for store_name in store_names:
            store = store_map[store_name]

            existing_price = (
                db.query(Price)
                .filter_by(game_id=game.id, store_id=store.id)
                .first()
            )
            if existing_price:
                continue

            discount = random.randint(10, 75)
            current_price = round(original_price * (1 - discount / 100), 2)

            price = Price(
                game_id=game.id,
                store_id=store.id,
                original_price=original_price,
                current_price=current_price,
                discount_percent=discount,
                deal_url=f"{store_map[store_name].url}/game/{slug}",
                last_updated=now,
            )
            db.add(price)
            prices_created += 1

            for i in range(5):
                days_ago = 30 - (i * 6)
                variation = random.uniform(-0.10, 0.10)
                historical_price = round(
                    current_price + (original_price - current_price) * (days_ago / 30) + variation * original_price,
                    2,
                )
                historical_price = max(historical_price, current_price * 0.9)

                history_entry = PriceHistory(
                    game_id=game.id,
                    store_id=store.id,
                    price=historical_price,
                    recorded_at=now - timedelta(days=days_ago),
                )
                db.add(history_entry)
                history_created += 1

    db.commit()
    db.close()

    print("=" * 50)
    print("SEED COMPLETADO")
    print("=" * 50)
    print(f"Tiendas insertadas:   {stores_created}")
    print(f"Juegos insertados:    {games_created}")
    print(f"Precios insertados:   {prices_created}")
    print(f"Historial insertado:  {history_created}")
    print("=" * 50)


if __name__ == "__main__":
    seed()
