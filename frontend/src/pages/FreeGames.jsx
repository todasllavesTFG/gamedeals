import { useState } from 'react';
import { useFetch } from '../hooks/useFetch';
import { getFreeGames } from '../lib/api';
import GameCard from '../components/ui/GameCard';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';

const SOURCES = [
  { value: 'all', label: 'Todos' },
  { value: 'epic', label: 'Epic Games' },
  { value: 'gamerpower', label: 'GamerPower' },
];

export default function FreeGames() {
  const [source, setSource] = useState('all');

  const { data, loading, error, refetch } = useFetch(
    (signal) => getFreeGames({ source }, signal),
    [source]
  );

  const games = data?.games ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-display font-semibold text-text">Juegos gratis</h1>
        {data && (
          <span className="text-text-muted text-sm">{data.total ?? games.length} juegos</span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-border">
        {SOURCES.map((s) => (
          <button
            key={s.value}
            onClick={() => setSource(s.value)}
            className={`px-4 py-2 text-sm font-medium transition-colors -mb-px border-b-2 cursor-pointer ${
              source === s.value
                ? 'border-accent text-accent'
                : 'border-transparent text-text-muted hover:text-text'
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} variant="card" />)}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={refetch} />}

      {!loading && !error && games.length === 0 && (
        <EmptyState text="No hay juegos gratis disponibles ahora mismo" />
      )}

      {!loading && !error && games.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {games.map((game) => (
            <GameCard
              key={game.deal_url || game.title}
              variant="free"
              title={game.title}
              image={game.image_url}
              currentPrice={game.current_price}
              originalPrice={game.original_price}
              storeName={game.store}
              dealUrl={game.deal_url}
            />
          ))}
        </div>
      )}
    </div>
  );
}
