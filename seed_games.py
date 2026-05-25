"""
seed_games.py — Inserta 80 juegos populares en la BD de GameDeals.
Añade también entradas en prices (Steam + GOG donde aplica).
Salta duplicados por slug.
"""

import re
import sqlite3
from datetime import datetime, timezone

DB_PATH = "C:/Users/Bernardo/Documents/clavetodo/backend/gamedeals.db"

NOW = datetime.now(timezone.utc).isoformat()

# ── 80 juegos populares ────────────────────────────────────────────────────────
# (titulo, plataforma, genero, metacritic, steam_app_id, precio_original, precio_actual, descuento, tiendas)
# tiendas: lista de ('NombreTienda', precio_original, precio_actual, descuento, url)
GAMES = [
    # ── Puzzle / Plataformas ──────────────────────────────────────────────
    ("Portal",              "PC", "Puzzle",        95, "400",     9.99,  2.49, 75,
     [("Steam", 9.99, 2.49, 75, "https://store.steampowered.com/app/400"),
      ("GOG",   9.99, 2.99, 70, "https://www.gog.com/game/portal")]),

    ("Portal 2",            "PC", "Puzzle",        95, "620",     9.99,  2.49, 75,
     [("Steam", 9.99, 2.49, 75, "https://store.steampowered.com/app/620"),
      ("GOG",   9.99, 2.99, 70, "https://www.gog.com/game/portal_2")]),

    ("Ori and the Blind Forest", "PC", "Plataformas", 88, "387290", 19.99, 3.99, 80,
     [("Steam", 19.99, 3.99, 80, "https://store.steampowered.com/app/387290")]),

    ("Ori and the Will of the Wisps", "PC", "Plataformas", 90, "1057090", 29.99, 11.99, 60,
     [("Steam", 29.99, 11.99, 60, "https://store.steampowered.com/app/1057090")]),

    ("Cuphead",             "PC", "Plataformas",   88, "268910",  19.99, 13.99, 30,
     [("Steam", 19.99, 13.99, 30, "https://store.steampowered.com/app/268910")]),

    ("Shovel Knight: Treasure Trove", "PC", "Plataformas", 90, "250760", 24.99, 12.49, 50,
     [("Steam", 24.99, 12.49, 50, "https://store.steampowered.com/app/250760"),
      ("GOG",   24.99, 12.49, 50, "https://www.gog.com/game/shovel_knight_treasure_trove")]),

    ("Undertale",           "PC", "RPG",           92, "391540",   9.99,  9.99,  0,
     [("Steam", 9.99, 9.99, 0, "https://store.steampowered.com/app/391540"),
      ("GOG",   9.99, 9.99, 0, "https://www.gog.com/game/undertale")]),

    ("Katana ZERO",         "PC", "Acción",        89, "1109900", 12.99,  7.79, 40,
     [("Steam", 12.99, 7.79, 40, "https://store.steampowered.com/app/1109900")]),

    # ── Acción / FPS ─────────────────────────────────────────────────────
    ("Half-Life 2",         "PC", "FPS",           96, "220",      9.99,  1.99, 80,
     [("Steam", 9.99, 1.99, 80, "https://store.steampowered.com/app/220")]),

    ("DOOM (2016)",         "PC", "FPS",           85, "379720",  19.99,  4.99, 75,
     [("Steam", 19.99, 4.99, 75, "https://store.steampowered.com/app/379720"),
      ("GOG",   19.99, 4.99, 75, "https://www.gog.com/game/doom_2016")]),

    ("DOOM Eternal",        "PC", "FPS",           88, "782330",  39.99,  9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/782330")]),

    ("Wolfenstein II: The New Colossus", "PC", "FPS", 87, "612880", 39.99, 5.99, 85,
     [("Steam", 39.99, 5.99, 85, "https://store.steampowered.com/app/612880")]),

    ("BioShock Remastered", "PC", "FPS",           96, "409710",  19.99,  4.99, 75,
     [("Steam", 19.99, 4.99, 75, "https://store.steampowered.com/app/409710"),
      ("GOG",   19.99, 4.99, 75, "https://www.gog.com/game/bioshock_remastered")]),

    ("BioShock Infinite",   "PC", "FPS",           94, "8870",    29.99,  7.49, 75,
     [("Steam", 29.99, 7.49, 75, "https://store.steampowered.com/app/8870")]),

    ("Ghostrunner",         "PC", "Acción",        80, "1139900", 29.99,  7.49, 75,
     [("Steam", 29.99, 7.49, 75, "https://store.steampowered.com/app/1139900"),
      ("GOG",   29.99, 7.49, 75, "https://www.gog.com/game/ghostrunner")]),

    ("Superhot",            "PC", "Acción",        82, "617830",  24.99,  6.24, 75,
     [("Steam", 24.99, 6.24, 75, "https://store.steampowered.com/app/617830")]),

    ("Hotline Miami",       "PC", "Acción",        83, "219150",   9.99,  2.49, 75,
     [("Steam", 9.99, 2.49, 75, "https://store.steampowered.com/app/219150"),
      ("GOG",   9.99, 2.49, 75, "https://www.gog.com/game/hotline_miami")]),

    # ── RPG / Action-RPG ─────────────────────────────────────────────────
    ("Grand Theft Auto V",  "PC", "Acción",        97, "271590",  29.99, 14.99, 50,
     [("Steam", 29.99, 14.99, 50, "https://store.steampowered.com/app/271590")]),

    ("The Elder Scrolls V: Skyrim SE", "PC", "RPG", 96, "489830", 39.99, 9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/489830"),
      ("GOG",   39.99, 9.99, 75, "https://www.gog.com/game/the_elder_scrolls_v_skyrim_special_edition")]),

    ("Dark Souls III",      "PC", "Action RPG",    89, "374320",  59.99, 14.99, 75,
     [("Steam", 59.99, 14.99, 75, "https://store.steampowered.com/app/374320")]),

    ("Sekiro: Shadows Die Twice", "PC", "Action RPG", 90, "814380", 59.99, 29.99, 50,
     [("Steam", 59.99, 29.99, 50, "https://store.steampowered.com/app/814380")]),

    ("Monster Hunter: World", "PC", "Action RPG",  90, "582010",  29.99,  7.49, 75,
     [("Steam", 29.99, 7.49, 75, "https://store.steampowered.com/app/582010")]),

    ("Monster Hunter Rise", "PC", "Action RPG",    87, "1446780", 39.99, 15.99, 60,
     [("Steam", 39.99, 15.99, 60, "https://store.steampowered.com/app/1446780")]),

    ("Divinity: Original Sin 2", "PC", "RPG",      93, "435150",  44.99, 13.49, 70,
     [("Steam", 44.99, 13.49, 70, "https://store.steampowered.com/app/435150"),
      ("GOG",   44.99, 13.49, 70, "https://www.gog.com/game/divinity_original_sin_2")]),

    ("Baldur's Gate 3",     "PC", "RPG",           96, "1086940", 59.99, 59.99,  0,
     [("Steam", 59.99, 59.99, 0, "https://store.steampowered.com/app/1086940"),
      ("GOG",   59.99, 59.99, 0, "https://www.gog.com/game/baldurs_gate_3")]),

    ("Mass Effect Legendary Edition", "PC", "RPG", 87, "1328670", 59.99, 14.99, 75,
     [("Steam", 59.99, 14.99, 75, "https://store.steampowered.com/app/1328670")]),

    ("Fallout 4",           "PC", "RPG",           84, "377160",  19.99,  3.99, 80,
     [("Steam", 19.99, 3.99, 80, "https://store.steampowered.com/app/377160")]),

    ("Fallout: New Vegas",  "PC", "RPG",           84, "22380",    9.99,  2.49, 75,
     [("Steam", 9.99, 2.49, 75, "https://store.steampowered.com/app/22380"),
      ("GOG",   9.99, 2.49, 75, "https://www.gog.com/game/fallout_new_vegas_ultimate_edition")]),

    ("Borderlands 2",       "PC", "FPS/RPG",       89, "49520",   19.99,  4.99, 75,
     [("Steam", 19.99, 4.99, 75, "https://store.steampowered.com/app/49520")]),

    ("Metal Gear Solid V: The Phantom Pain", "PC", "Acción", 95, "287700", 19.99, 3.99, 80,
     [("Steam", 19.99, 3.99, 80, "https://store.steampowered.com/app/287700")]),

    ("NieR: Automata",      "PC", "Action RPG",    88, "524220",  39.99,  9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/524220")]),

    ("Persona 4 Golden",    "PC", "RPG",           93, "1113000", 19.99,  9.99, 50,
     [("Steam", 19.99, 9.99, 50, "https://store.steampowered.com/app/1113000")]),

    ("Persona 5 Royal",     "PC", "RPG",           95, "1687950", 59.99, 39.99, 33,
     [("Steam", 59.99, 39.99, 33, "https://store.steampowered.com/app/1687950")]),

    ("Yakuza: Like a Dragon", "PC", "RPG",         87, "1235140", 59.99, 17.99, 70,
     [("Steam", 59.99, 17.99, 70, "https://store.steampowered.com/app/1235140")]),

    ("Dragon's Dogma 2",    "PC", "Action RPG",    86, "2054970", 59.99, 47.99, 20,
     [("Steam", 59.99, 47.99, 20, "https://store.steampowered.com/app/2054970")]),

    ("Final Fantasy XV Windows Edition", "PC", "RPG", 81, "637650", 24.99, 6.24, 75,
     [("Steam", 24.99, 6.24, 75, "https://store.steampowered.com/app/637650")]),

    ("God of War",          "PC", "Action RPG",    94, "1593500", 49.99, 24.99, 50,
     [("Steam", 49.99, 24.99, 50, "https://store.steampowered.com/app/1593500")]),

    # ── Horror / Survival ────────────────────────────────────────────────
    ("Resident Evil 4 Remake", "PC", "Survival Horror", 93, "2050650", 59.99, 29.99, 50,
     [("Steam", 59.99, 29.99, 50, "https://store.steampowered.com/app/2050650")]),

    ("Resident Evil Village", "PC", "Survival Horror", 84, "1196590", 39.99, 9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/1196590")]),

    ("Dead by Daylight",    "PC", "Survival",      79, "381210",  19.99,  4.99, 75,
     [("Steam", 19.99, 4.99, 75, "https://store.steampowered.com/app/381210")]),

    ("Subnautica",          "PC", "Aventura",      87, "264710",  29.99,  7.49, 75,
     [("Steam", 29.99, 7.49, 75, "https://store.steampowered.com/app/264710"),
      ("GOG",   29.99, 7.49, 75, "https://www.gog.com/game/subnautica")]),

    ("Rust",                "PC", "Supervivencia", 69, "252490",  39.99, 23.99, 40,
     [("Steam", 39.99, 23.99, 40, "https://store.steampowered.com/app/252490")]),

    ("Don't Starve Together", "PC", "Supervivencia", 87, "322330", 14.99, 7.49, 50,
     [("Steam", 14.99, 7.49, 50, "https://store.steampowered.com/app/322330")]),

    # ── Roguelike / Indie ────────────────────────────────────────────────
    ("Slay the Spire",      "PC", "Roguelike",     89, "646570",  24.99, 12.49, 50,
     [("Steam", 24.99, 12.49, 50, "https://store.steampowered.com/app/646570"),
      ("GOG",   24.99, 12.49, 50, "https://www.gog.com/game/slay_the_spire")]),

    ("Dead Cells",          "PC", "Roguelike",     89, "588650",  24.99,  6.24, 75,
     [("Steam", 24.99, 6.24, 75, "https://store.steampowered.com/app/588650"),
      ("GOG",   24.99, 6.24, 75, "https://www.gog.com/game/dead_cells")]),

    ("Vampire Survivors",   "PC", "Roguelike",     88, "1794680",  4.99,  3.99, 20,
     [("Steam", 4.99, 3.99, 20, "https://store.steampowered.com/app/1794680")]),

    ("Returnal",            "PC", "Roguelike",     86, "1649240", 59.99, 39.99, 33,
     [("Steam", 59.99, 39.99, 33, "https://store.steampowered.com/app/1649240")]),

    ("Outer Wilds",         "PC", "Aventura",      85, "753640",  24.99, 14.99, 40,
     [("Steam", 24.99, 14.99, 40, "https://store.steampowered.com/app/753640"),
      ("GOG",   24.99, 14.99, 40, "https://www.gog.com/game/outer_wilds")]),

    ("The Stanley Parable: Ultra Deluxe", "PC", "Aventura", 89, "1703340", 17.99, 12.59, 30,
     [("Steam", 17.99, 12.59, 30, "https://store.steampowered.com/app/1703340"),
      ("GOG",   17.99, 12.59, 30, "https://www.gog.com/game/the_stanley_parable_ultra_deluxe")]),

    ("Among Us",            "PC", "Estrategia",    85, "945360",   3.99,  3.19, 20,
     [("Steam", 3.99, 3.19, 20, "https://store.steampowered.com/app/945360")]),

    ("Terraria",            "PC", "Aventura",      83, "105600",   9.99,  4.99, 50,
     [("Steam", 9.99, 4.99, 50, "https://store.steampowered.com/app/105600"),
      ("GOG",   9.99, 4.99, 50, "https://www.gog.com/game/terraria")]),

    ("No Man's Sky",        "PC", "Aventura",      84, "275850",  59.99, 29.99, 50,
     [("Steam", 59.99, 29.99, 50, "https://store.steampowered.com/app/275850")]),

    # ── Stealth / Inmersive Sim ───────────────────────────────────────────
    ("Dishonored 2",        "PC", "Acción",        79, "403640",  29.99,  5.99, 80,
     [("Steam", 29.99, 5.99, 80, "https://store.steampowered.com/app/403640"),
      ("GOG",   29.99, 5.99, 80, "https://www.gog.com/game/dishonored_2")]),

    ("Prey (2017)",         "PC", "Acción/RPG",    79, "480490",  29.99,  4.49, 85,
     [("Steam", 29.99, 4.49, 85, "https://store.steampowered.com/app/480490"),
      ("GOG",   29.99, 4.49, 85, "https://www.gog.com/game/prey")]),

    ("Deus Ex: Mankind Divided", "PC", "Action RPG", 84, "337000", 29.99, 5.99, 80,
     [("Steam", 29.99, 5.99, 80, "https://store.steampowered.com/app/337000"),
      ("GOG",   29.99, 5.99, 80, "https://www.gog.com/game/deus_ex_mankind_divided")]),

    ("Control Ultimate Edition", "PC", "Acción",   82, "870780",  29.99,  5.99, 80,
     [("Steam", 29.99, 5.99, 80, "https://store.steampowered.com/app/870780"),
      ("GOG",   29.99, 5.99, 80, "https://www.gog.com/game/control_ultimate_edition")]),

    ("Alan Wake 2",         "PC", "Acción/Terror", 89, "1903780", 59.99, 39.99, 33,
     [("Steam", 59.99, 39.99, 33, "https://store.steampowered.com/app/1903780")]),

    ("Death Stranding",     "PC", "Acción",        82, "1190460", 39.99,  9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/1190460")]),

    # ── Lucha / Deportes ─────────────────────────────────────────────────
    ("Devil May Cry 5",     "PC", "Acción",        88, "601150",  29.99,  7.49, 75,
     [("Steam", 29.99, 7.49, 75, "https://store.steampowered.com/app/601150")]),

    ("Street Fighter 6",    "PC", "Lucha",         92, "1837780", 59.99, 35.99, 40,
     [("Steam", 59.99, 35.99, 40, "https://store.steampowered.com/app/1837780")]),

    ("Mortal Kombat 11",    "PC", "Lucha",         79, "976310",  49.99,  7.49, 85,
     [("Steam", 49.99, 7.49, 85, "https://store.steampowered.com/app/976310")]),

    ("Tekken 8",            "PC", "Lucha",         91, "1778820", 59.99, 41.99, 30,
     [("Steam", 59.99, 41.99, 30, "https://store.steampowered.com/app/1778820")]),

    ("Forza Horizon 5",     "PC", "Carreras",      92, "1551360", 59.99, 29.99, 50,
     [("Steam", 59.99, 29.99, 50, "https://store.steampowered.com/app/1551360")]),

    ("Rocket League",       "PC", "Deportes",      86, "252950",  19.99, 19.99,  0,
     [("Steam", 19.99, 19.99, 0, "https://store.steampowered.com/app/252950")]),

    # ── Simulación / Estrategia ───────────────────────────────────────────
    ("Factorio",            "PC", "Estrategia",    90, "427520",  30.00, 30.00,  0,
     [("Steam", 30.00, 30.00, 0, "https://store.steampowered.com/app/427520")]),

    ("RimWorld",            "PC", "Estrategia",    88, "294100",  34.99, 34.99,  0,
     [("Steam", 34.99, 34.99, 0, "https://store.steampowered.com/app/294100")]),

    ("Satisfactory",        "PC", "Simulación",    88, "526870",  34.99, 26.24, 25,
     [("Steam", 34.99, 26.24, 25, "https://store.steampowered.com/app/526870")]),

    ("Cities: Skylines",    "PC", "Simulación",    85, "255710",  27.99,  5.59, 80,
     [("Steam", 27.99, 5.59, 80, "https://store.steampowered.com/app/255710")]),

    ("Euro Truck Simulator 2", "PC", "Simulación", 79, "227300",  19.99,  3.99, 80,
     [("Steam", 19.99, 3.99, 80, "https://store.steampowered.com/app/227300")]),

    ("Crusader Kings III",  "PC", "Estrategia",    91, "1158310", 49.99, 24.99, 50,
     [("Steam", 49.99, 24.99, 50, "https://store.steampowered.com/app/1158310")]),

    ("Hearts of Iron IV",   "PC", "Estrategia",    87, "394360",  39.99,  9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/394360")]),

    ("Stellaris",           "PC", "Estrategia",    78, "281990",  39.99,  9.99, 75,
     [("Steam", 39.99, 9.99, 75, "https://store.steampowered.com/app/281990")]),

    ("Total War: WARHAMMER III", "PC", "Estrategia", 78, "1142710", 59.99, 14.99, 75,
     [("Steam", 59.99, 14.99, 75, "https://store.steampowered.com/app/1142710")]),

    ("Age of Empires II: Definitive Edition", "PC", "Estrategia", 87, "813780", 19.99, 4.99, 75,
     [("Steam", 19.99, 4.99, 75, "https://store.steampowered.com/app/813780")]),

    ("Age of Empires IV",   "PC", "Estrategia",    81, "1466860", 59.99, 29.99, 50,
     [("Steam", 59.99, 29.99, 50, "https://store.steampowered.com/app/1466860")]),

    # ── Cooperativo ───────────────────────────────────────────────────────
    ("It Takes Two",        "PC", "Cooperativo",   94, "1426210", 39.99, 19.99, 50,
     [("Steam", 39.99, 19.99, 50, "https://store.steampowered.com/app/1426210")]),

    ("Overcooked! 2",       "PC", "Cooperativo",   82, "728880",  21.99,  5.49, 75,
     [("Steam", 21.99, 5.49, 75, "https://store.steampowered.com/app/728880")]),

    ("ARK: Survival Evolved", "PC", "Supervivencia", 70, "346110", 59.99, 11.99, 80,
     [("Steam", 59.99, 11.99, 80, "https://store.steampowered.com/app/346110")]),

    # ── Sandbox / Mundo Abierto ───────────────────────────────────────────
    ("The Witcher 2: Assassins of Kings", "PC", "RPG", 88, "20920", 19.99, 2.99, 85,
     [("Steam", 19.99, 2.99, 85, "https://store.steampowered.com/app/20920"),
      ("GOG",   19.99, 1.99, 90, "https://www.gog.com/game/the_witcher_2")]),

    ("Kingdom Come: Deliverance", "PC", "RPG",     76, "379430",  29.99,  4.49, 85,
     [("Steam", 29.99, 4.49, 85, "https://store.steampowered.com/app/379430"),
      ("GOG",   29.99, 4.49, 85, "https://www.gog.com/game/kingdom_come_deliverance")]),

    ("Assassin's Creed Odyssey", "PC", "Acción",   85, "812140",  59.99,  8.99, 85,
     [("Steam", 59.99, 8.99, 85, "https://store.steampowered.com/app/812140")]),

    ("Horizon Zero Dawn Complete Edition", "PC", "Action RPG", 89, "1151640", 49.99, 9.99, 80,
     [("Steam", 49.99, 9.99, 80, "https://store.steampowered.com/app/1151640")]),

    ("Spider-Man Remastered", "PC", "Acción",      87, "1817070", 59.99, 35.99, 40,
     [("Steam", 59.99, 35.99, 40, "https://store.steampowered.com/app/1817070")]),

    ("Cyberpunk 2077: Phantom Liberty", "PC", "RPG", 90, "2054985", 29.99, 20.99, 30,
     [("Steam", 29.99, 20.99, 30, "https://store.steampowered.com/app/2054985")]),

    ("Red Dead Redemption 2 (Standalone)", "PC", "Acción", 93, "1174180", 59.99, 23.99, 60,
     [("Steam", 59.99, 23.99, 60, "https://store.steampowered.com/app/1174180")]),
]


def slugify(title):
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def get_or_create_store(cur, name):
    cur.execute("SELECT id FROM stores WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO stores (name, is_scraper) VALUES (?, 0)",
        (name,)
    )
    return cur.lastrowid


def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Obtener slugs existentes para saltar duplicados
    cur.execute("SELECT slug FROM games")
    existing_slugs = {r[0] for r in cur.fetchall()}

    inserted_games  = 0
    skipped_games   = 0
    inserted_prices = 0

    for entry in GAMES:
        title, plat, genre, meta, steam_id, orig, curr, disc, stores = entry
        slug = slugify(title)

        if slug in existing_slugs:
            skipped_games += 1
            continue

        cur.execute(
            """INSERT INTO games
               (title, slug, platform, genre, metacritic_score, steam_app_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, slug, plat, genre, meta, steam_id, NOW, NOW)
        )
        game_id = cur.lastrowid
        existing_slugs.add(slug)
        inserted_games += 1

        for store_name, s_orig, s_curr, s_disc, s_url in stores:
            store_id = get_or_create_store(cur, store_name)
            cur.execute(
                """INSERT OR IGNORE INTO prices
                   (game_id, store_id, original_price, current_price, discount_percent, deal_url, last_updated)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (game_id, store_id, s_orig, s_curr, s_disc, s_url, NOW)
            )
            cur.execute(
                """INSERT INTO price_history
                   (game_id, store_id, price, recorded_at)
                   VALUES (?, ?, ?, ?)""",
                (game_id, store_id, s_curr, NOW)
            )
            inserted_prices += 1

    conn.commit()
    conn.close()

    print(f"Juegos insertados:  {inserted_games}")
    print(f"Juegos saltados:    {skipped_games}  (ya existían)")
    print(f"Entradas de precio: {inserted_prices}")

    # Verificación final
    conn2 = sqlite3.connect(DB_PATH)
    total = conn2.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    conn2.close()
    print(f"\nTotal juegos en BD: {total}")


if __name__ == "__main__":
    main()
