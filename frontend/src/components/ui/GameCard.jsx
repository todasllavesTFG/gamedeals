import { useNavigate } from 'react-router-dom';
import { ImageOff, ExternalLink } from 'lucide-react';
import PriceBadge from './PriceBadge';
import StoreIcon from './StoreIcon';
import WishlistButton from './WishlistButton';

export default function GameCard({
  title,
  image,
  currentPrice,
  originalPrice,
  discount,
  storeName,
  dealUrl,
  gameId,
  variant,
}) {
  const navigate = useNavigate();

  const handleCardClick = () => {
    if (gameId) navigate(`/games/${gameId}`);
    else if (dealUrl) window.open(dealUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <div
      onClick={handleCardClick}
      className="group relative rounded-xl overflow-hidden bg-surface border border-border cursor-pointer
                 transition-all duration-200 hover:scale-[1.02] hover:shadow-glow-accent hover:border-accent/40
                 flex flex-col"
    >
      {/* Image */}
      <div className="aspect-video relative overflow-hidden bg-surface-2">
        {image ? (
          <img
            src={image}
            alt={title}
            loading="lazy"
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
              e.currentTarget.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div
          className="absolute inset-0 items-center justify-center bg-surface-2"
          style={{ display: image ? 'none' : 'flex' }}
        >
          <ImageOff className="w-8 h-8 text-text-muted" />
        </div>

        {gameId && (
          <div className="absolute top-2 left-2 z-10">
            <WishlistButton gameId={gameId} />
          </div>
        )}

        {/* Badge overlay */}
        <div className="absolute top-2 right-2">
          {variant === 'free' ? (
            <span className="bg-warning text-bg text-xs font-bold px-2 py-0.5 rounded">
              GRATIS
            </span>
          ) : (
            discount && (
              <span className="bg-accent text-bg text-xs font-bold px-2 py-0.5 rounded">
                -{Math.round(discount)}%
              </span>
            )
          )}
        </div>
      </div>

      {/* Body */}
      <div className="p-3 flex flex-col gap-1.5 flex-1">
        <h3 className="text-text text-sm font-medium line-clamp-2 leading-snug">{title}</h3>

        {variant !== 'free' && (
          <PriceBadge original={originalPrice} current={currentPrice} discount={discount} />
        )}
      </div>

      {/* Footer */}
      <div className="px-3 pb-3 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <StoreIcon storeName={storeName || ''} />
          <span className="text-text-muted text-xs truncate max-w-24">{storeName}</span>
        </div>
        {dealUrl && (
          <a
            href={dealUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-text-muted hover:text-accent transition-colors"
            title="Ver en tienda"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  );
}
