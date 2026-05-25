import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import { useFetch } from '../hooks/useFetch';
import { getDeals, getFreeGames } from '../lib/api';
import { formatPrice } from '../lib/format';
import GameCard from '../components/ui/GameCard';
import PriceBadge from '../components/ui/PriceBadge';
import Skeleton from '../components/ui/Skeleton';
import ErrorState from '../components/ui/ErrorState';

function HeroSection() {
  const { data, loading, error, refetch } = useFetch(
    (signal) => getDeals({ sortBy: 'discount', limit: 3 }, signal),
    []
  );

  if (loading) return <Skeleton variant="hero" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!data || data.length === 0) return null;

  const deal = data[0];

  return (
    <section
      className="relative w-full h-80 sm:h-96 rounded-2xl overflow-hidden mb-10 flex items-end"
      style={{
        backgroundImage: deal.game?.image_url ? `url(${deal.game.image_url})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundColor: 'var(--color-surface)',
      }}
    >
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-bg via-bg/60 to-transparent" />

      <div className="relative z-10 p-6 sm:p-8 flex flex-col gap-3">
        <h1 className="font-display text-3xl sm:text-5xl font-bold text-text leading-tight">
          {deal.game?.title}
        </h1>
        <PriceBadge
          original={deal.original_price}
          current={deal.current_price}
          discount={deal.discount_percent}
          size="lg"
        />
        <a
          href={deal.deal_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 self-start mt-1 px-5 py-2.5 rounded-lg
                     bg-accent text-bg font-semibold text-sm hover:brightness-110 transition-all"
        >
          Ver oferta <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </section>
  );
}

function BestDealsSection() {
  const { data, loading, error, refetch } = useFetch(
    (signal) => getDeals({ sortBy: 'discount', limit: 6 }, signal),
    []
  );

  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-display font-semibold text-text">Mejores ofertas hoy</h2>
        <Link to="/deals" className="text-accent text-sm hover:underline">
          Ver todas →
        </Link>
      </div>

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} variant="card" />)}
        </div>
      )}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && data && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.map((deal) => (
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
    </section>
  );
}

function FreeGamesSection() {
  const { data, loading, error, refetch } = useFetch(
    (signal) => getFreeGames({ source: 'all' }, signal),
    []
  );

  const games = data?.games?.slice(0, 4) ?? [];

  return (
    <section className="mb-12">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-display font-semibold text-text">Gratis esta semana</h2>
        <Link to="/free" className="text-accent text-sm hover:underline">
          Ver todos →
        </Link>
      </div>

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} variant="card" />)}
        </div>
      )}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && games.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
    </section>
  );
}

export default function Home() {
  return (
    <>
      <HeroSection />
      <BestDealsSection />
      <FreeGamesSection />
    </>
  );
}
