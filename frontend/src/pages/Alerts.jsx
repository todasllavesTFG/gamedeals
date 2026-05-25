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
