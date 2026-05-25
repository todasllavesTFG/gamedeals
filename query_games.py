import sqlite3

conn = sqlite3.connect('C:/Users/Bernardo/Documents/clavetodo/backend/gamedeals.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM games')
total = cur.fetchone()[0]
print('Total juegos en la BD:', total)
print()

cur.execute('''
    SELECT g.id, g.title, g.platform, g.genre, g.metacritic_score, g.steam_app_id,
           MIN(p.current_price) as best_price,
           MAX(p.discount_percent) as best_discount
    FROM games g
    LEFT JOIN prices p ON p.game_id = g.id
    GROUP BY g.id
    ORDER BY g.title
''')
rows = cur.fetchall()

print(f"{'ID':<6} | {'Titulo':<50} | {'Plat':<5} | {'Meta':<5} | {'Precio':<8} | {'Dto%':<5} | Steam AppID")
print('-' * 110)
for r in rows:
    gid, title, plat, genre, meta, steam, price, disc = r
    title = (title or '')[:49]
    plat  = (plat  or '-')[:5]
    meta  = str(meta) if meta else '-'
    steam = (steam or '-')[:12]
    price_s = f"{price:.2f}E" if price is not None else '-'
    disc_s  = f"{disc}%" if disc is not None else '-'
    print(f"{gid:<6} | {title:<50} | {plat:<5} | {meta:<5} | {price_s:<8} | {disc_s:<5} | {steam}")

conn.close()
