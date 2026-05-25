import { Link } from 'react-router-dom';
import { Heart } from 'lucide-react';
import { useWishlist } from '../context/WishlistContext';
import GameCard from '../components/ui/GameCard';
import EmptyState from '../components/ui/EmptyState';

export default function Wishlist() {
  const { items } = useWishlist();
  if (!items.length) {
    return (
      <div className="py-16">
        <EmptyState text="Tu wishlist está vacía" icon={Heart} />
        <div className="text-center mt-4">
          <Link to="/deals" className="text-[var(--color-accent)] hover:underline">Ver ofertas</Link>
        </div>
      </div>
    );
  }
  return (
    <div>
      <h1 className="font-display text-2xl sm:text-3xl font-bold text-[var(--color-text)] mb-6">Mi wishlist</h1>
      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
        {items.map(item => (
          <GameCard
            key={item.game_id}
            gameId={item.game.id}
            title={item.game.title}
            image={item.game.image_url}
            currentPrice={item.best_price?.current_price}
            originalPrice={item.best_price?.current_price}
            discount={item.best_price?.discount_percent}
            storeName={item.best_price?.store_name}
            dealUrl={item.best_price?.deal_url}
          />
        ))}
      </div>
    </div>
  );
}
