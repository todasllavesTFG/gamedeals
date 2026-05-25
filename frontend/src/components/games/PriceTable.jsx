import { useMemo } from 'react';
import { ExternalLink } from 'lucide-react';
import StoreIcon from '../ui/StoreIcon';
import { formatPrice, formatDiscount } from '../../lib/format';

export default function PriceTable({ prices = [] }) {
  const sorted = useMemo(
    () => [...prices].sort((a, b) => a.current_price - b.current_price),
    [prices]
  );

  if (sorted.length === 0) return null;

  return (
    <>
      {/* Desktop table */}
      <div className="hidden sm:block overflow-hidden rounded-2xl border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-2 text-text-muted text-left">
              <th className="px-4 py-3 font-medium">Tienda</th>
              <th className="px-4 py-3 font-medium">Precio actual</th>
              <th className="px-4 py-3 font-medium">Original</th>
              <th className="px-4 py-3 font-medium">Descuento</th>
              <th className="px-4 py-3 font-medium">Acción</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((price, i) => (
              <tr
                key={price.store_name + i}
                className={`border-t border-border transition-colors hover:bg-surface-2 ${
                  i === 0 ? 'bg-accent/5 border-l-4 border-l-accent' : ''
                }`}
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <StoreIcon storeName={price.store_name} />
                    <span className="text-text">{price.store_name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 font-semibold text-text">
                  {formatPrice(price.current_price)}
                </td>
                <td className="px-4 py-3 text-text-muted line-through">
                  {price.original_price > price.current_price
                    ? formatPrice(price.original_price)
                    : '—'}
                </td>
                <td className="px-4 py-3">
                  {price.discount_percent > 0 ? (
                    <span className="text-xs font-bold bg-accent text-bg px-1.5 py-0.5 rounded">
                      {formatDiscount(price.discount_percent)}
                    </span>
                  ) : (
                    <span className="text-text-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  {price.deal_url ? (
                    <a
                      href={price.deal_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-text-muted hover:text-accent transition-colors text-xs"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      Ver oferta
                    </a>
                  ) : (
                    <span className="text-text-muted">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="sm:hidden space-y-2">
        {sorted.map((price, i) => (
          <div
            key={price.store_name + i}
            className={`rounded-xl border p-4 ${
              i === 0
                ? 'border-accent/40 bg-accent/5 border-l-4 border-l-accent'
                : 'border-border bg-surface'
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <StoreIcon storeName={price.store_name} />
                <span className="text-text text-sm font-medium">{price.store_name}</span>
              </div>
              <div className="flex items-center gap-2">
                {price.discount_percent > 0 && (
                  <span className="text-xs font-bold bg-accent text-bg px-1.5 py-0.5 rounded">
                    {formatDiscount(price.discount_percent)}
                  </span>
                )}
                <span className="font-semibold text-text">{formatPrice(price.current_price)}</span>
                {price.deal_url && (
                  <a
                    href={price.deal_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-text-muted hover:text-accent transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
            {price.original_price > price.current_price && (
              <p className="text-xs text-text-muted mt-1 ml-8">
                Antes: <span className="line-through">{formatPrice(price.original_price)}</span>
              </p>
            )}
          </div>
        ))}
      </div>
    </>
  );
}
