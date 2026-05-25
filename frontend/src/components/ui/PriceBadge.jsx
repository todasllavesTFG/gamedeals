import { formatPrice, formatDiscount } from '../../lib/format';

export default function PriceBadge({ original, current, discount, size = 'sm' }) {
  const big = size === 'lg';

  if (discount) {
    return (
      <div className={`flex items-center gap-1.5 flex-wrap ${big ? 'text-base' : 'text-xs'}`}>
        <span className={`bg-accent text-bg font-bold rounded px-1.5 py-0.5 ${big ? 'text-sm' : 'text-xs'}`}>
          {formatDiscount(discount)}
        </span>
        <span className={`text-text font-semibold ${big ? 'text-xl' : ''}`}>
          {formatPrice(current)}
        </span>
        <span className="text-text-muted line-through">
          {formatPrice(original)}
        </span>
      </div>
    );
  }

  return (
    <span className={`text-text font-semibold ${big ? 'text-xl' : 'text-sm'}`}>
      {formatPrice(current)}
    </span>
  );
}
