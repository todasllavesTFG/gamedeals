import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { ImageOff, ChevronDown, ChevronUp } from 'lucide-react';
import { useFetch } from '../hooks/useFetch';
import { getGame } from '../lib/api';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';
import BestPriceCTA from '../components/games/BestPriceCTA';
import PriceTable from '../components/games/PriceTable';
import PriceHistoryChart from '../components/games/PriceHistoryChart';

function MetacriticBadge({ score }) {
  if (!score) return null;
  const color =
    score >= 75 ? 'text-green-400 border-green-400/40 bg-green-400/10'
    : score >= 50 ? 'text-yellow-400 border-yellow-400/40 bg-yellow-400/10'
    : 'text-red-400 border-red-400/40 bg-red-400/10';
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-bold border rounded px-1.5 py-0.5 ${color}`}>
      MC {score}
    </span>
  );
}

export default function GameDetail() {
  const { id } = useParams();
  const { data: game, loading, error, refetch } = useFetch(
    (signal) => getGame(id, signal),
    [id]
  );
  const [expanded, setExpanded] = useState(false);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="hero" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} variant="card" />)}
        </div>
      </div>
    );
  }

  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!game) return null;

  const prices = game.prices ?? game.deals ?? [];
  const allTimeLowPrice =
    typeof game.all_time_low === 'number'
      ? game.all_time_low
      : game.all_time_low?.price ?? null;

  const description = game.description || game.short_description || '';
  const showToggle = description.length > 300;

  return (
    <div className="space-y-8 pb-12">
      {/* Hero */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Imagen */}
        <div className="lg:col-span-2 aspect-video rounded-2xl overflow-hidden bg-surface-2 flex-shrink-0">
          {game.image_url ? (
            <img
              src={game.image_url}
              alt={game.title}
              className="w-full h-full object-cover"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <ImageOff className="w-12 h-12 text-text-muted" />
            </div>
          )}
        </div>

        {/* Metadatos */}
        <div className="lg:col-span-3 flex flex-col gap-3">
          <h1 className="font-display text-2xl sm:text-3xl font-bold text-text leading-tight">
            {game.title}
          </h1>

          <div className="flex flex-wrap items-center gap-2">
            <MetacriticBadge score={game.metacritic_score} />
            {game.genres?.map((g) => (
              <span
                key={g}
                className="text-xs px-2 py-0.5 rounded-full bg-surface-2 text-text-muted border border-border"
              >
                {g}
              </span>
            ))}
            {game.platform && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-surface-2 text-text-muted border border-border">
                {game.platform}
              </span>
            )}
          </div>

          {description && (
            <div>
              <p
                className={`text-sm text-text-muted leading-relaxed ${
                  !expanded && showToggle ? 'line-clamp-6' : ''
                }`}
              >
                {description}
              </p>
              {showToggle && (
                <button
                  onClick={() => setExpanded((v) => !v)}
                  className="flex items-center gap-1 text-xs text-accent hover:underline mt-1"
                >
                  {expanded ? (
                    <>Leer menos <ChevronUp className="w-3 h-3" /></>
                  ) : (
                    <>Leer más <ChevronDown className="w-3 h-3" /></>
                  )}
                </button>
              )}
            </div>
          )}

          {allTimeLowPrice != null && (
            <p className="text-xs text-text-muted">
              Mínimo histórico:{' '}
              <span className="text-accent font-semibold">
                {Number(allTimeLowPrice).toFixed(2)} €
              </span>
            </p>
          )}
        </div>
      </div>

      {/* Mejor precio CTA */}
      {game.best_price && (
        <BestPriceCTA
          bestPrice={game.best_price}
          allTimeLowPrice={allTimeLowPrice}
        />
      )}

      {/* Tabla comparativa */}
      {prices.length > 0 && (
        <section className="space-y-4">
          <h2 className="font-display text-lg font-semibold text-text">
            Comparativa de precios
          </h2>
          <PriceTable prices={prices} />
        </section>
      )}

      {/* Historial de precios */}
      <section className="space-y-4">
        <h2 className="font-display text-lg font-semibold text-text">
          Historial de precios
        </h2>
        <div className="rounded-2xl border border-border bg-surface p-4">
          <PriceHistoryChart
            gameId={id}
            allTimeLow={allTimeLowPrice != null ? { price: allTimeLowPrice } : null}
          />
        </div>
      </section>
    </div>
  );
}
