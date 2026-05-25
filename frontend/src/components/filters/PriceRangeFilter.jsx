export default function PriceRangeFilter({ minPrice, maxPrice, onChange }) {
  return (
    <div>
      <p className="text-text-muted text-xs font-medium uppercase tracking-wider mb-2">Rango de precio (€)</p>
      <div className="flex items-center gap-2">
        <input
          type="number"
          min="0"
          step="0.01"
          placeholder="Mín"
          value={minPrice ?? ''}
          onChange={(e) => onChange({ minPrice: e.target.value === '' ? undefined : Number(e.target.value), maxPrice })}
          className="w-full bg-surface-2 border border-border text-text text-sm rounded-lg px-3 py-2
                     focus:outline-none focus:ring-2 focus:ring-accent/50"
        />
        <span className="text-text-muted text-sm flex-shrink-0">—</span>
        <input
          type="number"
          min="0"
          step="0.01"
          placeholder="Máx"
          value={maxPrice ?? ''}
          onChange={(e) => onChange({ minPrice, maxPrice: e.target.value === '' ? undefined : Number(e.target.value) })}
          className="w-full bg-surface-2 border border-border text-text text-sm rounded-lg px-3 py-2
                     focus:outline-none focus:ring-2 focus:ring-accent/50"
        />
      </div>
    </div>
  );
}
