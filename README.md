# GameDeals

> Comparador de ofertas de videojuegos — Trabajo de Fin de Grado (2.º DAM)

GameDeals es una aplicación web que agrega y compara precios de videojuegos de varias tiendas digitales, muestra el historial de precios de cada juego, avisa cuando un juego baja de un precio objetivo y recopila los juegos gratis de la semana.

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend API | FastAPI 0.115 + Python 3.11 |
| ORM / Base de datos | SQLAlchemy 2.0 + SQLite |
| Autenticación | JWT (python-jose) + bcrypt |
| Tareas programadas | APScheduler 3.x |
| Scrapers | BeautifulSoup4 (Fanatical) · Playwright (Humble Bundle) |
| Frontend | React 19 + Vite 8 |
| Estilos | Tailwind CSS 4 |
| Gráficas | Recharts |

## Funcionalidades

- Catálogo de ofertas con filtros por tienda, precio máximo, descuento mínimo y plataforma.
- Buscador con debounce y autocompletado.
- Ficha de juego: metadatos (descripción, géneros, Metacritic), tabla comparativa de precios por tienda y gráfica de historial de precios con mínimo histórico.
- Juegos gratis de Epic Games Store y GamerPower.
- Wishlist personal con contador en navbar.
- Alertas de precio: recibe un email cuando el juego baja de tu precio objetivo. Agrupadas por estado (activa / pausada / disparada).
- Autenticación completa: registro, login, rutas protegidas (JWT en localStorage).
- Actualización automática de precios cada hora (APScheduler).

## Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior

## Instalacion

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

### Frontend

```powershell
cd frontend
npm install
```

## Arrancar el proyecto

Necesitas dos terminales abiertas a la vez.

Terminal 1 — Backend:
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```
API disponible en http://localhost:8000
Swagger UI en http://localhost:8000/docs

Terminal 2 — Frontend:
```powershell
cd frontend
npm run dev
```
Aplicación web en http://localhost:5173

## Variables de entorno

Crea el archivo backend/.env:

```env
RAWG_API_KEY=tu_clave_rawg
JWT_SECRET_KEY=cambia-esto-por-una-clave-segura
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=tu_app_password
```

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /deals | Listado de ofertas (filtros: store_id, max_price, min_discount, platform, sortBy, page, limit) |
| GET | /games/{id} | Ficha de juego con historial de precios |
| GET | /games/{id}/price-history | Historial de precios del juego |
| GET | /free | Juegos gratis activos |
| GET | /search?q= | Búsqueda de juegos |
| GET | /stores | Lista de tiendas |
| POST | /auth/register | Registro de usuario |
| POST | /auth/login | Login — devuelve JWT |
| GET | /wishlist | Wishlist del usuario autenticado |
| POST | /wishlist/{game_id} | Añadir juego a wishlist |
| DELETE | /wishlist/{game_id} | Eliminar de wishlist |
| GET | /alerts | Alertas del usuario autenticado |
| POST | /alerts | Crear alerta de precio |
| PATCH | /alerts/{id} | Actualizar alerta (target_price, is_active) |
| DELETE | /alerts/{id} | Eliminar alerta |

## Estructura del proyecto

```
clavetodo/
├── backend/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── scheduler.py
│       ├── models/
│       ├── schemas/
│       ├── routers/
│       └── services/
│           ├── cheapshark.py
│           ├── steam.py
│           ├── rawg.py
│           ├── epic.py
│           ├── gamerpower.py
│           ├── fanatical.py
│           ├── humble.py
│           └── email.py
└── frontend/
    └── src/
        ├── App.jsx
        ├── context/
        ├── hooks/
        ├── lib/
        │   └── api.js
        ├── pages/
        └── components/
            ├── layout/
            └── ui/
```

## Autor

Bernardo González — 2.º DAM
TFG · Curso 2025–2026
