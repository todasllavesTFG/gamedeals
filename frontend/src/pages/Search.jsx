import { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFetch } from '../hooks/useFetch';
import { useDebounce } from '../hooks/useDebounce';
import { searchDeals, getDeals } from '../lib/api';
import GameCard from '../components/ui/GameCard';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';
import EmptyState from '../components/ui/EmptyState';
import FilterSidebar from '../components/filters/FilterSidebar';

const DEFAULT_FILTERS = {
  platforms: [],
  genre: '',
  minPrice: undefined,
  maxPrice: undefined,
  minDiscount: 0,
  sortBy: 'discount',
};

export default function Search() {
  const [searchParams] = useSearchParams();
  const q = searchParams.get('q') || '';
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const debouncedQ = useDebounce(q, 300);

  const { data, loading, error, refetch } = useFetch(
    (signal) =>
      debouncedQ.length >= 2
        ? searchDeals(debouncedQ, signal)
        : getDeals({ sortBy: filters.sortBy, limit: 50 }, signal),
    [debouncedQ, filters.sortBy]
  );

  const results = useMemo(() => {
    if (!data) return [];

    return data.filter((deal) => {
      const price = deal.current_price ?? 0;
      const discount = deal.discount_percent ?? 0;
      const platform = deal.game?.platform ?? '';

      if (filters.platforms.length > 0) {
        const match = filters.platforms.some((p) =>
          platform.toLowerCase().includes(p.toLowerCase())
        );
        if (!match) return false;
      }

      if (filters.minPrice != null && price < filters.minPrice) return false;
      if (filters.maxPrice != null && price > filters.maxPrice) return false;
      if (filters.minDiscount > 0 && discount < filters.minDiscount) return false;

      return true;
    });
  }, [data, filters]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold text-text">
          {debouncedQ ? `Resultados para «${debouncedQ}»` : 'Buscar juegos'}
        </h1>
        {!loading && results.length > 0 && (
          <p className="text-text-muted text-sm mt-1">{results.length} resultado{results.length !== 1 ? 's' : ''}</p>
        )}
      </div>

      <div className="flex gap-6 items-start">
        {/* Sidebar */}
        <div className="hidden md:block w-64 flex-shrink-0">
          <FilterSidebar filters={filters} onChange={setFilters} />
        </div>

        {/* Results */}
        <div className="flex-1 min-w-0">
          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 9 }).map((_, i) => <Skeleton key={i} variant="card" />)}
            </div>
          )}

          {error && <ErrorState message={error} onRetry={refetch} />}

          {!loading && !error && results.length === 0 && (
            <EmptyState
              text={debouncedQ ? `Sin resultados para «${debouncedQ}»` : 'Introduce un término de búsqueda'}
            />
          )}

          {!loading && !error && results.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((deal) => (
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
          )}
        </div>
      </div>
    </div>
  );
}
