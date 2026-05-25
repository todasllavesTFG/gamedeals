import { Heart } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useWishlist } from '../../context/WishlistContext';

export default function WishlistButton({ gameId, className = '' }) {
  const { isAuthenticated } = useAuth();
  const { isInWishlist, toggle } = useWishlist();
  if (!isAuthenticated || !gameId) return null;
  const inList = isInWishlist(gameId);
  return (
    <button
      onClick={(e) => { e.stopPropagation(); e.preventDefault(); toggle(gameId); }}
      aria-label={inList ? 'Quitar de wishlist' : 'Añadir a wishlist'}
      className={`p-1.5 rounded-full bg-black/60 backdrop-blur border border-white/10 hover:bg-black/80 transition-colors cursor-pointer ${className}`}
    >
      <Heart className={`w-4 h-4 transition-colors ${inList ? 'fill-[var(--color-accent)] text-[var(--color-accent)]' : 'text-white/60'}`} />
    </button>
  );
}
