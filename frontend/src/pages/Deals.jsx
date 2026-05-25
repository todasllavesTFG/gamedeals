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
