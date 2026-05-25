# Plan de Implementación — Días 18, 19 y 20
## GameDeals TFG · Sistema de alertas de precio + Panel de alertas + Deals con filtros avanzados

> **Cómo usar este documento:** Entrega cada PASO a Claude Code en orden. El código está completo y listo para escribir a disco. No necesitas pensar — solo copia el paso, Claude Code lo ejecuta.

---

## RESUMEN DE ARCHIVOS

| Paso | Archivo | Acción | Día |
|------|---------|--------|-----|
| 1 | `backend/app/schemas/alerts.py` | CREAR | 18 |
| 2 | `backend/app/services/email.py` | CREAR | 18 |
| 3 | `backend/app/routers/alerts.py` | CREAR | 18 |
| 4 | `backend/app/scheduler.py` | EDITAR | 18 |
| 5 | `backend/app/main.py` | EDITAR | 18 |
| 6 | `backend/app/routers/deals.py` | EDITAR | 20 |
| 7 | `frontend/src/lib/api.js` | EDITAR | 19+20 |
| 8 | `frontend/src/pages/Alerts.jsx` | CREAR | 19 |
| 9 | `frontend/src/App.jsx` | EDITAR | 19 |
| 10 | `frontend/src/components/layout/Navbar.jsx` | EDITAR | 19 |
| 11 | `frontend/src/pages/Deals.jsx` | EDITAR | 20 |

---

## DÍA 18 — Sistema de alertas de precio (Backend)

---

### PASO 1 — CREAR `backend/app/schemas/alerts.py`

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    game_id: int
    target_price: float = Field(..., gt=0, description="Precio objetivo en euros")


class AlertUpdate(BaseModel):
    target_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class AlertOut(BaseModel):
    id: int
    game_id: int
    target_price: float
    is_active: bool
    is_triggered: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    # Campos enriquecidos (calculados en el router)
    game_title: Optional[str] = None
    game_image: Optional[str] = None
    current_best_price: Optional[float] = None
    best_store_name: Optional[str] = None

    model_config = {"from_attributes": True}
```

---

### PASO 2 — CREAR `backend/app/services/email.py`

```python
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "") or SMTP_USER


def send_price_alert_email(
    to_email: str,
    username: str,
    game_title: str,
    target_price: float,
    current_price: float,
    store_name: str,
    deal_url: str,
) -> bool:
    """
    Envía un email de alerta de precio al usuario.

    Si SMTP_HOST o SMTP_USER no están configurados, simula el envío
    logueando el evento (no lanza excepción — never fail silently).

    Returns True si el email se envió (o se simuló), False si hubo un
    error real de red/autenticación.
    """
    subject = f"🎮 Alerta GameDeals: {game_title} por {current_price:.2f}€"

    html_body = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:'Inter',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:32px 16px;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0"
             style="background:#14141f;border-radius:12px;border:1px solid #2a2a3d;overflow:hidden;">

        <!-- Header -->
        <tr>
          <td style="background:#1c1c2b;padding:24px 32px;border-bottom:1px solid #2a2a3d;">
            <span style="font-size:1.1rem;font-weight:700;color:#a3ff12;letter-spacing:0.05em;">
              🎮 GameDeals
            </span>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px;">
            <h1 style="margin:0 0 8px 0;font-size:1.3rem;color:#e8e8f0;">
              ¡Tu alerta se ha disparado!
            </h1>
            <p style="margin:0 0 24px 0;color:#8b8ba3;font-size:0.9rem;">
              Hola <strong style="color:#e8e8f0;">{username}</strong>,
              el juego que estabas esperando ya está por debajo de tu precio objetivo.
            </p>

            <!-- Game card -->
            <div style="background:#1c1c2b;border-radius:8px;padding:20px;
                        border:1px solid #2a2a3d;margin-bottom:24px;">
              <p style="margin:0 0 4px 0;font-size:1rem;font-weight:600;color:#e8e8f0;">
                {game_title}
              </p>
              <p style="margin:0 0 12px 0;font-size:0.8rem;color:#8b8ba3;">
                en {store_name}
              </p>
              <div style="display:flex;align-items:baseline;gap:12px;">
                <span style="font-size:1.75rem;font-weight:700;color:#a3ff12;">
                  {current_price:.2f}€
                </span>
                <span style="font-size:0.85rem;color:#8b8ba3;">
                  Tu objetivo: {target_price:.2f}€
                </span>
              </div>
            </div>

            <!-- CTA -->
            <a href="{deal_url}"
               style="display:inline-block;background:#a3ff12;color:#0a0a0f;
                      padding:12px 28px;border-radius:8px;text-decoration:none;
                      font-weight:700;font-size:0.95rem;">
              Ver oferta →
            </a>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:16px 32px;border-top:1px solid #2a2a3d;">
            <p style="margin:0;font-size:0.75rem;color:#8b8ba3;">
              Recibes este email porque configuraste una alerta en GameDeals.
              La alerta ha sido desactivada automáticamente.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""

    # Sin configuración SMTP → simular y devolver OK
    if not SMTP_HOST or not SMTP_USER:
        logger.info(
            "[EMAIL SIMULADO] to=%s | juego='%s' | precio=%.2f€ | objetivo=%.2f€ | tienda=%s",
            to_email,
            game_title,
            current_price,
            target_price,
            store_name,
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to_email], msg.as_string())

        logger.info(
            "Email de alerta enviado a %s para '%s' (%.2f€)",
            to_email,
            game_title,
            current_price,
        )
        return True

    except Exception:
        logger.exception("Error enviando email de alerta a %s", to_email)
        return False
```

---

### PASO 3 — CREAR `backend/app/routers/alerts.py`

```python
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
```

---

### PASO 4 — EDITAR `backend/app/scheduler.py`

Hay dos cambios:

**4a) Añadir estos imports al principio del archivo (después de los imports existentes):**

```python
# Añadir a la sección de imports de app.models:
from app.models.alerts import Alert
from app.models.users import User
```

**4b) Añadir esta función ANTES de `register_jobs()`:**

```python
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
        # (los joins de arriba ya los carga, pero refreshamos las relaciones)
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
```

**4c) Dentro de `register_jobs()`, añadir este bloque ANTES del `logger.info` final:**

```python
    scheduler.add_job(
        check_price_alerts,
        trigger="interval",
        minutes=30,
        id="check_price_alerts",
        name="Comprobación alertas de precio",
        next_run_time=now + timedelta(seconds=30),
        replace_existing=True,
    )
```

**4d) Actualizar el mensaje del `logger.info` al final de `register_jobs()` para incluir el nuevo job:**

```python
    logger.info(
        "Jobs registrados: cheapshark_prices (1h), steam_prices (2h), "
        "fanatical_prices (6h), humble_bundles (6h), check_price_alerts (30min)"
    )
```

---

### PASO 5 — EDITAR `backend/app/main.py`

**5a) Añadir este import junto a los demás imports de routers:**

```python
from app.routers import alerts
```

**5b) Añadir esta línea después de `app.include_router(wishlist.router)`:**

```python
app.include_router(alerts.router)
```

El bloque de includes quedará así al final:

```python
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(deals.router)
app.include_router(games.router)
app.include_router(free_games.router)
app.include_router(admin.router)
app.include_router(wishlist.router)
app.include_router(alerts.router)  # ← NUEVO
```

---

## DÍA 20 — Filtros avanzados en Deals (Backend primero, luego Frontend)

---

### PASO 6 — EDITAR `backend/app/routers/deals.py`

Reemplazar el archivo completo con esta versión (conserva toda la lógica existente + añade filtros):

```python
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, contains_eager

from app.database import get_db
from app.models.games import Game
from app.models.prices import Price
from app.models.stores import Store
from app.services.cheapshark import fetch_deals_from_api, save_deals_to_db

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
            "image_url": p.game.image_url,
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
```

---

## DÍA 19 — Panel de alertas (Frontend)

---

### PASO 7 — EDITAR `frontend/src/lib/api.js`

Reemplazar el archivo completo con esta versión (conserva todo lo existente + añade alertas y filtros en deals):

```javascript
const BASE = import.meta.env.VITE_API_URL;
const TOKEN_KEY = 'gamedeals_token';

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

async function request(path, { signal, method = 'GET', body, isForm, json } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let fetchBody;
  if (isForm) {
    fetchBody = body instanceof URLSearchParams ? body : new URLSearchParams(body);
  } else if (json) {
    headers['Content-Type'] = 'application/json';
    fetchBody = JSON.stringify(body);
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: fetchBody,
    ...(signal ? { signal } : {}),
  });

  if (res.status === 401) {
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
  }

  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch (_) {}
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }

  if (res.status === 204) return null;
  return res.json();
}

// ── Deals ────────────────────────────────────────────────────────────────────

/**
 * Obtiene deals con soporte de filtros avanzados.
 * @param {object} opts
 * @param {number}  [opts.page=0]         - Página (0-based)
 * @param {number}  [opts.limit=12]       - Resultados por página
 * @param {string}  [opts.sortBy='discount'] - 'discount' | 'price' | 'title'
 * @param {number}  [opts.storeId]        - ID de tienda
 * @param {number}  [opts.maxPrice]       - Precio máximo (€)
 * @param {number}  [opts.minDiscount]    - Descuento mínimo (%)
 * @param {string}  [opts.platform]       - Plataforma (texto parcial)
 */
export function getDeals(
  { page = 0, limit = 12, sortBy = 'discount', storeId, maxPrice, minDiscount, platform } = {},
  signal
) {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
    sort_by: sortBy,
  });
  if (storeId != null)      params.set('store_id', String(storeId));
  if (maxPrice != null)     params.set('max_price', String(maxPrice));
  if (minDiscount != null)  params.set('min_discount', String(minDiscount));
  if (platform)             params.set('platform', platform);
  return request(`/deals?${params}`, { signal });
}

export function searchDeals(q, signal) {
  return request(`/deals/search?q=${encodeURIComponent(q)}`, { signal });
}

export function getStores(signal) {
  return request('/deals/stores', { signal });
}

// ── Games ────────────────────────────────────────────────────────────────────

export function getGame(id, signal) {
  return request(`/games/${id}`, { signal });
}

export function getGameHistory(id, { storeId, days } = {}, signal) {
  const params = new URLSearchParams();
  if (storeId) params.set('store_id', storeId);
  if (days) params.set('days', days);
  return request(`/games/${id}/history?${params}`, { signal });
}

// ── Free Games ───────────────────────────────────────────────────────────────

export function getFreeGames({ source = 'all', platform } = {}, signal) {
  const params = new URLSearchParams({ source });
  if (platform) params.set('platform', platform);
  return request(`/free-games?${params}`, { signal });
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export function register({ email, username, password }) {
  return request('/auth/register', {
    method: 'POST',
    json: true,
    body: { email, username, password },
  });
}

export function login({ email, password }) {
  return request('/auth/login', {
    method: 'POST',
    isForm: true,
    body: new URLSearchParams({ username: email, password }),
  });
}

export function getMe(signal) {
  return request('/auth/me', { signal });
}

// ── Wishlist ─────────────────────────────────────────────────────────────────

export function getWishlist(signal) {
  return request('/wishlist', { signal });
}

export function addToWishlist(gameId) {
  return request(`/wishlist/${gameId}`, { method: 'POST' });
}

export function removeFromWishlist(gameId) {
  return request(`/wishlist/${gameId}`, { method: 'DELETE' });
}

// ── Alerts ───────────────────────────────────────────────────────────────────

/** Obtiene todas las alertas del usuario autenticado */
export function getAlerts(signal) {
  return request('/alerts', { signal });
}

/**
 * Crea una nueva alerta de precio
 * @param {{ game_id: number, target_price: number }} body
 */
export function createAlert(body) {
  return request('/alerts', { method: 'POST', json: true, body });
}

/**
 * Actualiza el precio objetivo o el estado activo de una alerta
 * @param {number} alertId
 * @param {{ target_price?: number, is_active?: boolean }} body
 */
export function updateAlert(alertId, body) {
  return request(`/alerts/${alertId}`, { method: 'PATCH', json: true, body });
}

/** Elimina permanentemente una alerta */
export function deleteAlert(alertId) {
  return request(`/alerts/${alertId}`, { method: 'DELETE' });
}
```

---

### PASO 8 — CREAR `frontend/src/pages/Alerts.jsx`

```jsx
import { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, Plus, Trash2, PauseCircle, PlayCircle, Search, X, CheckCircle } from 'lucide-react';
import { getAlerts, createAlert, updateAlert, deleteAlert, searchDeals } from '../lib/api';

// ─────────────────────────────────────────────────────────────
// Sub-componente: Modal para crear una nueva alerta
// ─────────────────────────────────────────────────────────────
function CreateAlertModal({ onClose, onCreated }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selectedGame, setSelectedGame] = useState(null);
  const [targetPrice, setTargetPrice] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const searchTimeout = useRef(null);

  // Búsqueda con debounce de 350ms
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(async () => {
      setSearching(true);
      try {
        const data = await searchDeals(query);
        // Deduplicar por game.id — solo nos interesa el juego, no la tienda
        const seen = new Set();
        const unique = data.filter((d) => {
          if (seen.has(d.game.id)) return false;
          seen.add(d.game.id);
          return true;
        });
        setResults(unique.slice(0, 8));
      } catch (_) {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 350);
    return () => clearTimeout(searchTimeout.current);
  }, [query]);

  const handleSelectGame = (deal) => {
    setSelectedGame(deal.game);
    // Sugerir el precio actual como punto de partida
    setTargetPrice(deal.current_price ? String(deal.current_price.toFixed(2)) : '');
    setQuery('');
    setResults([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedGame) return setError('Selecciona un juego');
    const price = parseFloat(targetPrice);
    if (isNaN(price) || price <= 0) return setError('Introduce un precio válido mayor que 0');

    setSubmitting(true);
    setError(null);
    try {
      const newAlert = await createAlert({ game_id: selectedGame.id, target_price: price });
      onCreated(newAlert);
      onClose();
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="w-full max-w-md rounded-xl border p-6 shadow-2xl"
        style={{
          background: 'var(--color-surface)',
          borderColor: 'var(--color-border)',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text)' }}>
            Nueva alerta de precio
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg transition-colors"
            style={{ color: 'var(--color-text-muted)' }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Juego seleccionado o buscador */}
          {selectedGame ? (
            <div
              className="flex items-center gap-3 rounded-lg p-3 border"
              style={{ background: 'var(--color-surface-2)', borderColor: 'var(--color-border)' }}
            >
              {selectedGame.image_url && (
                <img
                  src={selectedGame.image_url}
                  alt={selectedGame.title}
                  className="w-10 h-10 rounded object-cover flex-shrink-0"
                />
              )}
              <span className="flex-1 text-sm font-medium" style={{ color: 'var(--color-text)' }}>
                {selectedGame.title}
              </span>
              <button
                type="button"
                onClick={() => { setSelectedGame(null); setTargetPrice(''); }}
                className="p-1 rounded transition-colors"
                style={{ color: 'var(--color-text-muted)' }}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="relative">
              <div className="relative">
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
                  style={{ color: 'var(--color-text-muted)' }}
                />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Buscar juego..."
                  autoFocus
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg border text-sm
                             focus:outline-none focus:ring-2"
                  style={{
                    background: 'var(--color-surface-2)',
                    borderColor: 'var(--color-border)',
                    color: 'var(--color-text)',
                    '--tw-ring-color': 'color-mix(in srgb, var(--color-accent) 40%, transparent)',
                  }}
                />
              </div>

              {/* Dropdown de resultados */}
              {(results.length > 0 || searching) && (
                <div
                  className="absolute z-10 w-full mt-1 rounded-lg border overflow-hidden shadow-lg"
                  style={{
                    background: 'var(--color-surface)',
                    borderColor: 'var(--color-border)',
                  }}
                >
                  {searching && (
                    <div className="px-3 py-2 text-xs" style={{ color: 'var(--color-text-muted)' }}>
                      Buscando...
                    </div>
                  )}
                  {results.map((d) => (
                    <button
                      key={d.game.id}
                      type="button"
                      onClick={() => handleSelectGame(d)}
                      className="w-full flex items-center gap-2 px-3 py-2 text-left text-sm
                                 transition-colors hover:brightness-110"
                      style={{ color: 'var(--color-text)', background: 'var(--color-surface-2)' }}
                    >
                      {d.game.image_url && (
                        <img
                          src={d.game.image_url}
                          alt={d.game.title}
                          className="w-7 h-7 rounded object-cover flex-shrink-0"
                        />
                      )}
                      <span className="flex-1 truncate">{d.game.title}</span>
                      <span className="text-xs flex-shrink-0" style={{ color: 'var(--color-accent)' }}>
                        {d.current_price?.toFixed(2)}€
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Precio objetivo */}
          <div>
            <label
              className="block text-xs font-medium mb-1.5"
              style={{ color: 'var(--color-text-muted)' }}
            >
              Precio objetivo (€)
            </label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="ej: 9.99"
              className="w-full px-3 py-2.5 rounded-lg border text-sm focus:outline-none focus:ring-2"
              style={{
                background: 'var(--color-surface-2)',
                borderColor: 'var(--color-border)',
                color: 'var(--color-text)',
                '--tw-ring-color': 'color-mix(in srgb, var(--color-accent) 40%, transparent)',
              }}
            />
            <p className="mt-1 text-xs" style={{ color: 'var(--color-text-muted)' }}>
              Recibirás un email cuando el precio baje de esta cifra.
            </p>
          </div>

          {/* Error */}
          {error && (
            <p className="text-xs" style={{ color: 'var(--color-danger)' }}>{error}</p>
          )}

          {/* Acciones */}
          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-lg border text-sm font-medium transition-colors"
              style={{
                borderColor: 'var(--color-border)',
                color: 'var(--color-text-muted)',
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting || !selectedGame}
              className="flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all
                         disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                background: 'var(--color-accent)',
                color: 'var(--color-bg)',
              }}
            >
              {submitting ? 'Creando...' : 'Crear alerta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Sub-componente: Tarjeta de alerta individual
// ─────────────────────────────────────────────────────────────
function AlertCard({ alert, onUpdate, onDelete }) {
  const [loading, setLoading] = useState(false);

  const isActive = alert.is_active && !alert.is_triggered;
  const isTriggered = alert.is_triggered;
  const isPaused = !alert.is_active && !alert.is_triggered;

  const priceBelowTarget =
    alert.current_best_price != null && alert.current_best_price <= alert.target_price;

  const handleToggle = async () => {
    setLoading(true);
    try {
      const updated = await updateAlert(alert.id, { is_active: !alert.is_active });
      onUpdate(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReactivate = async () => {
    setLoading(true);
    try {
      const updated = await updateAlert(alert.id, { is_active: true });
      onUpdate(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`¿Eliminar la alerta para "${alert.game_title}"?`)) return;
    setLoading(true);
    try {
      await deleteAlert(alert.id);
      onDelete(alert.id);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div
      className="rounded-xl border p-4 flex gap-3 transition-opacity"
      style={{
        background: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
        opacity: loading ? 0.6 : 1,
      }}
    >
      {/* Imagen del juego */}
      {alert.game_image ? (
        <img
          src={alert.game_image}
          alt={alert.game_title}
          className="w-14 h-14 rounded-lg object-cover flex-shrink-0"
        />
      ) : (
        <div
          className="w-14 h-14 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ background: 'var(--color-surface-2)' }}
        >
          <Bell className="w-6 h-6" style={{ color: 'var(--color-text-muted)' }} />
        </div>
      )}

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2 mb-1">
          <p
            className="text-sm font-semibold truncate flex-1"
            style={{ color: 'var(--color-text)' }}
          >
            {alert.game_title ?? `Juego #${alert.game_id}`}
          </p>

          {/* Badge de estado */}
          {isTriggered && (
            <span
              className="flex-shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
              style={{ background: 'color-mix(in srgb, var(--color-warning) 20%, transparent)', color: 'var(--color-warning)' }}
            >
              DISPARADA
            </span>
          )}
          {isActive && (
            <span
              className="flex-shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
              style={{ background: 'color-mix(in srgb, var(--color-accent) 15%, transparent)', color: 'var(--color-accent)' }}
            >
              ACTIVA
            </span>
          )}
          {isPaused && (
            <span
              className="flex-shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
              style={{ background: 'color-mix(in srgb, var(--color-text-muted) 15%, transparent)', color: 'var(--color-text-muted)' }}
            >
              PAUSADA
            </span>
          )}
        </div>

        {/* Precios */}
        <div className="flex items-baseline gap-3 mb-1">
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            Objetivo:
          </span>
          <span className="text-sm font-semibold" style={{ color: 'var(--color-accent)' }}>
            {alert.target_price.toFixed(2)}€
          </span>

          {alert.current_best_price != null && (
            <>
              <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                Mejor precio ahora:
              </span>
              <span
                className="text-sm font-medium"
                style={{ color: priceBelowTarget ? 'var(--color-accent)' : 'var(--color-text-muted)' }}
              >
                {alert.current_best_price.toFixed(2)}€
                {alert.best_store_name && (
                  <span className="text-xs ml-1" style={{ color: 'var(--color-text-muted)' }}>
                    ({alert.best_store_name})
                  </span>
                )}
              </span>
            </>
          )}
        </div>

        {/* Fecha de disparo */}
        {alert.triggered_at && (
          <p className="text-xs flex items-center gap-1" style={{ color: 'var(--color-text-muted)' }}>
            <CheckCircle className="w-3 h-3" style={{ color: 'var(--color-warning)' }} />
            Disparada el {new Date(alert.triggered_at).toLocaleDateString('es-ES')}
          </p>
        )}
      </div>

      {/* Acciones */}
      <div className="flex flex-col gap-1.5 flex-shrink-0">
        {/* Pausar/Reactivar (para activas y pausadas) */}
        {!isTriggered && (
          <button
            onClick={handleToggle}
            disabled={loading}
            title={isActive ? 'Pausar alerta' : 'Reactivar alerta'}
            className="p-1.5 rounded-lg transition-colors disabled:opacity-50"
            style={{
              color: isActive ? 'var(--color-text-muted)' : 'var(--color-accent)',
              background: 'var(--color-surface-2)',
            }}
          >
            {isActive ? <PauseCircle className="w-4 h-4" /> : <PlayCircle className="w-4 h-4" />}
          </button>
        )}

        {/* Reactivar (solo para disparadas) */}
        {isTriggered && (
          <button
            onClick={handleReactivate}
            disabled={loading}
            title="Reactivar alerta"
            className="p-1.5 rounded-lg transition-colors disabled:opacity-50"
            style={{ color: 'var(--color-accent)', background: 'var(--color-surface-2)' }}
          >
            <PlayCircle className="w-4 h-4" />
          </button>
        )}

        {/* Eliminar */}
        <button
          onClick={handleDelete}
          disabled={loading}
          title="Eliminar alerta"
          className="p-1.5 rounded-lg transition-colors disabled:opacity-50"
          style={{ color: 'var(--color-danger)', background: 'var(--color-surface-2)' }}
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Página principal de alertas
// ─────────────────────────────────────────────────────────────
export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    getAlerts(controller.signal)
      .then((data) => {
        setAlerts(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, []);

  const handleCreated = (newAlert) => {
    setAlerts((prev) => [newAlert, ...prev]);
  };

  const handleUpdate = (updated) => {
    setAlerts((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
  };

  const handleDelete = (alertId) => {
    setAlerts((prev) => prev.filter((a) => a.id !== alertId));
  };

  // Separar por estado para mostrarlas agrupadas
  const active = alerts.filter((a) => a.is_active && !a.is_triggered);
  const triggered = alerts.filter((a) => a.is_triggered);
  const paused = alerts.filter((a) => !a.is_active && !a.is_triggered);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1
            className="text-2xl font-display font-semibold"
            style={{ color: 'var(--color-text)' }}
          >
            Alertas de precio
          </h1>
          <p className="text-sm mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
            Recibe un email cuando un juego baje de tu precio objetivo
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold
                     transition-all hover:brightness-110"
          style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Nueva alerta</span>
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-20 rounded-xl animate-pulse"
              style={{ background: 'var(--color-surface)' }}
            />
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          className="rounded-xl p-4 text-sm"
          style={{
            background: 'color-mix(in srgb, var(--color-danger) 10%, transparent)',
            color: 'var(--color-danger)',
            border: '1px solid color-mix(in srgb, var(--color-danger) 30%, transparent)',
          }}
        >
          {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && alerts.length === 0 && (
        <div className="text-center py-16">
          <Bell
            className="w-12 h-12 mx-auto mb-4"
            style={{ color: 'var(--color-text-muted)' }}
          />
          <p className="font-medium mb-1" style={{ color: 'var(--color-text)' }}>
            Sin alertas configuradas
          </p>
          <p className="text-sm mb-6" style={{ color: 'var(--color-text-muted)' }}>
            Crea una alerta para recibir un email cuando un juego baje de precio
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="px-5 py-2.5 rounded-lg text-sm font-semibold transition-all hover:brightness-110"
            style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}
          >
            Crear mi primera alerta
          </button>
        </div>
      )}

      {/* Listas agrupadas */}
      {!loading && !error && alerts.length > 0 && (
        <div className="space-y-6">
          {/* Activas */}
          {active.length > 0 && (
            <section>
              <h2
                className="text-xs font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--color-text-muted)' }}
              >
                Activas ({active.length})
              </h2>
              <div className="space-y-3">
                {active.map((a) => (
                  <AlertCard
                    key={a.id}
                    alert={a}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Disparadas */}
          {triggered.length > 0 && (
            <section>
              <h2
                className="text-xs font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--color-text-muted)' }}
              >
                Disparadas ({triggered.length})
              </h2>
              <div className="space-y-3">
                {triggered.map((a) => (
                  <AlertCard
                    key={a.id}
                    alert={a}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Pausadas */}
          {paused.length > 0 && (
            <section>
              <h2
                className="text-xs font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--color-text-muted)' }}
              >
                Pausadas ({paused.length})
              </h2>
              <div className="space-y-3">
                {paused.map((a) => (
                  <AlertCard
                    key={a.id}
                    alert={a}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* Modal para crear alerta */}
      {showModal && (
        <CreateAlertModal
          onClose={() => setShowModal(false)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}
```

---

### PASO 9 — EDITAR `frontend/src/App.jsx`

Reemplazar el archivo completo:

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WishlistProvider } from './context/WishlistContext';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Deals from './pages/Deals';
import FreeGames from './pages/FreeGames';
import Search from './pages/Search';
import GameDetail from './pages/GameDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Wishlist from './pages/Wishlist';
import Alerts from './pages/Alerts';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WishlistProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/deals" element={<Deals />} />
              <Route path="/free" element={<FreeGames />} />
              <Route path="/search" element={<Search />} />
              <Route path="/games/:id" element={<GameDetail />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/wishlist" element={<Wishlist />} />
                <Route path="/alerts" element={<Alerts />} />
              </Route>
            </Route>
          </Routes>
        </WishlistProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

---

### PASO 10 — EDITAR `frontend/src/components/layout/Navbar.jsx`

Reemplazar el archivo completo:

```jsx
import { NavLink, Link } from 'react-router-dom';
import { Gamepad2, LogOut, Heart, Bell } from 'lucide-react';
import SearchBar from './SearchBar';
import { useAuth } from '../../context/AuthContext';
import { useWishlist } from '../../context/WishlistContext';

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/deals', label: 'Deals' },
  { to: '/free', label: 'Free' },
];

export default function Navbar() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { count } = useWishlist();

  return (
    <header className="sticky top-0 z-50 bg-bg/80 backdrop-blur border-b border-border">
      <div className="container mx-auto px-4 h-16 flex items-center gap-4">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2 flex-shrink-0">
          <Gamepad2 className="w-6 h-6 text-accent" />
          <span className="font-display text-accent font-semibold text-lg tracking-wide">
            GameDeals
          </span>
        </NavLink>

        {/* SearchBar */}
        <div className="flex-1 flex justify-center">
          <SearchBar />
        </div>

        {/* Nav links */}
        <nav className="flex items-center gap-1 flex-shrink-0">
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-accent/10 text-accent'
                    : 'text-text-muted hover:text-text hover:bg-surface-2'
                }`
              }
            >
              {label}
            </NavLink>
          ))}

          {/* Auth section */}
          {!loading && (
            isAuthenticated ? (
              <div className="flex items-center gap-2 ml-2">
                {/* Wishlist */}
                <Link
                  to="/wishlist"
                  className="relative p-2 rounded-lg transition-colors"
                  style={{ color: 'var(--color-text-muted)' }}
                  title="Mi wishlist"
                >
                  <Heart className="w-5 h-5" />
                  {count > 0 && (
                    <span
                      className="absolute -top-1 -right-1 text-[10px] font-bold rounded-full
                                 w-4 h-4 flex items-center justify-center"
                      style={{
                        background: 'var(--color-accent)',
                        color: 'var(--color-bg)',
                      }}
                    >
                      {count > 9 ? '9+' : count}
                    </span>
                  )}
                </Link>

                {/* Alertas ← NUEVO */}
                <Link
                  to="/alerts"
                  className="relative p-2 rounded-lg transition-colors"
                  style={{ color: 'var(--color-text-muted)' }}
                  title="Mis alertas de precio"
                >
                  <Bell className="w-5 h-5" />
                </Link>

                {/* Avatar */}
                <div
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
                  style={{ background: 'var(--color-surface-2)' }}
                >
                  <span
                    className="inline-flex items-center justify-center w-6 h-6 rounded-full
                               text-xs font-bold"
                    style={{
                      background: 'color-mix(in srgb, var(--color-accent) 20%, transparent)',
                      color: 'var(--color-accent)',
                    }}
                  >
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                  <span
                    className="text-sm font-medium hidden sm:block"
                    style={{ color: 'var(--color-text)' }}
                  >
                    {user?.username}
                  </span>
                </div>

                {/* Logout */}
                <button
                  onClick={logout}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm
                             font-medium transition-colors"
                  style={{ color: 'var(--color-text-muted)' }}
                  title="Cerrar sesión"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline">Salir</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1 ml-2">
                <NavLink
                  to="/login"
                  className="px-3 py-1.5 rounded-lg text-sm font-medium
                             text-text-muted hover:text-text hover:bg-surface-2 transition-colors"
                >
                  Login
                </NavLink>
                <NavLink
                  to="/register"
                  className="px-3 py-1.5 rounded-lg text-sm font-semibold
                             bg-accent text-bg hover:brightness-110 transition-all"
                >
                  Registrarse
                </NavLink>
              </div>
            )
          )}
        </nav>
      </div>
    </header>
  );
}
```

---

## DÍA 20 — Filtros avanzados en Deals (Frontend)

---

### PASO 11 — EDITAR `frontend/src/pages/Deals.jsx`

Reemplazar el archivo completo con esta versión que añade el panel de filtros avanzados:

```jsx
import { useState, useEffect, useCallback } from 'react';
import { SlidersHorizontal, X, ChevronDown } from 'lucide-react';
import { getDeals, getStores } from '../lib/api';
import GameCard from '../components/ui/GameCard';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';

const SORT_OPTIONS = [
  { value: 'discount', label: 'Mayor descuento' },
  { value: 'price', label: 'Menor precio' },
  { value: 'title', label: 'Título A-Z' },
];

const DISCOUNT_OPTIONS = [
  { value: '', label: 'Cualquier descuento' },
  { value: '10', label: '≥ 10%' },
  { value: '20', label: '≥ 20%' },
  { value: '30', label: '≥ 30%' },
  { value: '50', label: '≥ 50%' },
  { value: '70', label: '≥ 70%' },
  { value: '90', label: '≥ 90%' },
];

const PLATFORM_OPTIONS = [
  { value: '', label: 'Todas las plataformas' },
  { value: 'PC', label: 'PC' },
  { value: 'PlayStation', label: 'PlayStation' },
  { value: 'Xbox', label: 'Xbox' },
  { value: 'Nintendo', label: 'Nintendo' },
  { value: 'Mobile', label: 'Mobile' },
];

const PAGE_SIZE = 12;

// ── Estilos reutilizables ───────────────────────────────────────────────────
const inputStyle = {
  background: 'var(--color-surface-2)',
  borderColor: 'var(--color-border)',
  color: 'var(--color-text)',
};

function FilterSelect({ value, onChange, options, label }) {
  return (
    <div className="flex-1 min-w-[140px]">
      <label
        className="block text-[11px] font-medium uppercase tracking-wider mb-1"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border rounded-lg px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 cursor-pointer"
        style={inputStyle}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function FilterInput({ value, onChange, label, placeholder }) {
  return (
    <div className="flex-1 min-w-[120px]">
      <label
        className="block text-[11px] font-medium uppercase tracking-wider mb-1"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {label}
      </label>
      <input
        type="number"
        min="0"
        step="0.01"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
        style={inputStyle}
      />
    </div>
  );
}

// ── Página principal ────────────────────────────────────────────────────────
export default function Deals() {
  // Filtros
  const [sortBy, setSortBy] = useState('discount');
  const [storeId, setStoreId] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minDiscount, setMinDiscount] = useState('');
  const [platform, setPlatform] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(false);

  // Datos
  const [stores, setStores] = useState([]);
  const [allDeals, setAllDeals] = useState([]);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);

  // Cargar lista de tiendas (una sola vez)
  useEffect(() => {
    getStores()
      .then(setStores)
      .catch(() => {}); // silencioso — no bloquea la página
  }, []);

  // Helpers para construir el objeto de filtros actual
  const buildFilters = useCallback(
    (pageNum) => ({
      page: pageNum,
      limit: PAGE_SIZE,
      sortBy,
      storeId: storeId ? Number(storeId) : undefined,
      maxPrice: maxPrice !== '' ? Number(maxPrice) : undefined,
      minDiscount: minDiscount !== '' ? Number(minDiscount) : undefined,
      platform: platform || undefined,
    }),
    [sortBy, storeId, maxPrice, minDiscount, platform]
  );

  // Recarga desde cero cuando cambian los filtros
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    setAllDeals([]);
    setPage(0);
    setHasMore(true);

    getDeals(buildFilters(0), controller.signal)
      .then((data) => {
        setAllDeals(data);
        setHasMore(data.length === PAGE_SIZE);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [buildFilters]);

  const loadMore = () => {
    const nextPage = page + 1;
    setLoadingMore(true);
    getDeals(buildFilters(nextPage))
      .then((data) => {
        setAllDeals((prev) => [...prev, ...data]);
        setPage(nextPage);
        setHasMore(data.length === PAGE_SIZE);
        setLoadingMore(false);
      })
      .catch(() => setLoadingMore(false));
  };

  // ¿Hay algún filtro activo distinto del sort?
  const hasActiveFilters =
    storeId !== '' || maxPrice !== '' || minDiscount !== '' || platform !== '';

  const clearFilters = () => {
    setStoreId('');
    setMaxPrice('');
    setMinDiscount('');
    setPlatform('');
  };

  // Opciones de tiendas para el select
  const storeOptions = [
    { value: '', label: 'Todas las tiendas' },
    ...stores.map((s) => ({ value: String(s.id), label: s.name })),
  ];

  return (
    <div>
      {/* ── Header ──────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 mb-4">
        <h1
          className="text-2xl font-display font-semibold flex-1"
          style={{ color: 'var(--color-text)' }}
        >
          Todas las ofertas
        </h1>

        {/* Botón toggle filtros */}
        <button
          onClick={() => setFiltersOpen((v) => !v)}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm
                     font-medium transition-colors"
          style={{
            background: filtersOpen || hasActiveFilters
              ? 'color-mix(in srgb, var(--color-accent) 15%, transparent)'
              : 'var(--color-surface-2)',
            borderColor: hasActiveFilters ? 'var(--color-accent)' : 'var(--color-border)',
            color: hasActiveFilters ? 'var(--color-accent)' : 'var(--color-text-muted)',
          }}
        >
          <SlidersHorizontal className="w-4 h-4" />
          Filtros
          {hasActiveFilters && (
            <span
              className="ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
              style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}
            >
              ON
            </span>
          )}
          <ChevronDown
            className={`w-3.5 h-3.5 transition-transform ${filtersOpen ? 'rotate-180' : ''}`}
          />
        </button>

        {/* Ordenación */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 cursor-pointer"
          style={inputStyle}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* ── Panel de filtros (collapsible) ─────────────────────────── */}
      {filtersOpen && (
        <div
          className="rounded-xl border p-4 mb-5"
          style={{
            background: 'var(--color-surface)',
            borderColor: 'var(--color-border)',
          }}
        >
          <div className="flex flex-wrap gap-3">
            <FilterSelect
              label="Tienda"
              value={storeId}
              onChange={setStoreId}
              options={storeOptions}
            />
            <FilterInput
              label="Precio máximo (€)"
              value={maxPrice}
              onChange={setMaxPrice}
              placeholder="ej: 9.99"
            />
            <FilterSelect
              label="Descuento mínimo"
              value={minDiscount}
              onChange={setMinDiscount}
              options={DISCOUNT_OPTIONS}
            />
            <FilterSelect
              label="Plataforma"
              value={platform}
              onChange={setPlatform}
              options={PLATFORM_OPTIONS}
            />
          </div>

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="mt-3 flex items-center gap-1 text-xs font-medium transition-colors"
              style={{ color: 'var(--color-text-muted)' }}
            >
              <X className="w-3.5 h-3.5" />
              Limpiar filtros
            </button>
          )}
        </div>
      )}

      {/* ── Grid de deals ────────────────────────────────────────────── */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: PAGE_SIZE }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={clearFilters} />}

      {!loading && !error && allDeals.length === 0 && (
        <EmptyState
          text={
            hasActiveFilters
              ? 'Ninguna oferta coincide con los filtros'
              : 'No hay ofertas disponibles'
          }
        />
      )}

      {!loading && !error && allDeals.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {allDeals.map((deal) => (
              <GameCard
                key={deal.id}
                title={deal.game?.title}
                image={deal.game?.image_url}
                currentPrice={deal.current_price}
                originalPrice={deal.original_price}
                discount={deal.discount_percent}
                storeName={deal.store?.name}
                dealUrl={deal.deal_url}
                gameId={deal.game?.id}
              />
            ))}
          </div>

          {hasMore && (
            <div className="mt-8 flex justify-center">
              <button
                onClick={loadMore}
                disabled={loadingMore}
                className="px-6 py-2.5 rounded-lg border text-sm font-medium
                           transition-colors disabled:opacity-50 cursor-pointer"
                style={{
                  background: 'var(--color-surface-2)',
                  borderColor: 'var(--color-border)',
                  color: 'var(--color-text)',
                }}
              >
                {loadingMore ? 'Cargando...' : 'Cargar más'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
```

---

## CHECKLIST DE VERIFICACIÓN (ejecutar al final de cada día)

### Día 18 — Backend alertas
```bash
# Arrancar backend y comprobar que el router está disponible
cd backend
uvicorn app.main:app --reload

# Verificar endpoints (en otra terminal o browser)
curl http://localhost:8000/docs  # /alerts debe aparecer en la lista
```
Endpoints que deben aparecer en `/docs`:
- `GET  /alerts`
- `POST /alerts`
- `PATCH /alerts/{alert_id}`
- `DELETE /alerts/{alert_id}`

Verificar que el scheduler loguea el nuevo job:
```
Jobs registrados: ... check_price_alerts (30min)
```

### Día 19 — Frontend alertas
- Navegar a `http://localhost:5173/alerts` sin login → redirige a /login ✓
- Navegar con login → muestra la página de alertas ✓
- Icono Bell visible en Navbar ✓
- Crear alerta → buscar un juego → introducir precio → aparece en la lista ✓
- Pausar/Reactivar alerta → badge cambia ✓
- Eliminar alerta → desaparece de la lista ✓

### Día 20 — Deals con filtros
- Navegar a `http://localhost:5173/deals` ✓
- Botón "Filtros" abre el panel ✓
- Filtrar por tienda → el grid se actualiza ✓
- Filtrar por precio máximo → solo aparecen deals por debajo ✓
- Filtrar por descuento mínimo → solo aparecen deals con ese % o más ✓
- Limpiar filtros → vuelve al estado inicial ✓

---

## NOTAS IMPORTANTES

### Configuración SMTP (opcional para el email real)
Añadir estas variables al `.env` del backend para activar el envío real de emails:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASS=tu_app_password
SMTP_FROM=tu_email@gmail.com
```
**Sin estas variables**, el sistema funciona igual pero **loguea el email en vez de enviarlo** — perfecto para el TFG.

### Modelo Alert — campo is_triggered
El modelo existente `backend/app/models/alerts.py` tiene `is_triggered` (además del requerido `triggered_at`). El plan lo usa para la lógica del scheduler — no modificar el modelo.

### Bug conocido en paginación de Deals
El backend usa paginación 0-based (`page=0` = primera página). La versión anterior del frontend enviaba `page=1` por defecto, saltándose los primeros 12 resultados. El PASO 11 corrige esto cambiando el default a `page=0` en `getDeals()`.
