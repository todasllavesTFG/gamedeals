import { ExternalLink } from 'lucide-react';
import StoreIcon from '../ui/StoreIcon';
import { formatPrice, formatDiscount } from '../../lib/format';

export default function BestPriceCTA({ bestPrice, allTimeLowPrice }) {
  if (!bestPrice) return null;

  const isAllTimeLow =
    allTimeLowPrice != null && bestPrice.current_price <= allTimeLowPrice;

  return (
    <div className="rounded-2xl border border-accent/30 bg-gradient-to-r from-accent/10 to-violet/10 p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <StoreIcon storeName={bestPrice.store_name} />
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-text font-medium text-sm">{bestPrice.store_name}</span>
            {bestPrice.discount_percent > 0 && (
              <span className="text-xs font-bold bg-accent text-bg px-1.5 py-0.5 rounded">
                {formatDiscount(bestPrice.discount_percent)}
              </span>
            )}
            {isAllTimeLow && (
              <span className="text-xs font-bold bg-violet/80 text-white px-1.5 py-0.5 rounded uppercase tracking-wide">
                All-time low
              </span>
            )}
          </div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="font-display text-2xl font-bold text-accent">
              {formatPrice(bestPrice.current_price)}
            </span>
            {bestPrice.original_price > bestPrice.current_price && (
              <span className="text-sm line-through text-text-muted">
                {formatPrice(bestPrice.original_price)}
              </span>
            )}
          </div>
        </div>
      </div>

      {bestPrice.deal_url && (
        <a
          href={bestPrice.deal_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-accent text-bg font-semibold text-sm hover:brightness-110 hover:shadow-glow-accent transition-all flex-shrink-0"
        >
          <ExternalLink className="w-4 h-4" />
          Ir a la tienda
        </a>
      )}
    </div>
  );
}
