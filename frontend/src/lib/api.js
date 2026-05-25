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
