const SORT_OPTIONS = [
  { value: 'discount', label: 'Mayor descuento' },
  { value: 'price', label: 'Menor precio' },
  { value: 'title', label: 'Más reciente' },
];

export default function SortDropdown({ value = 'discount', onChange }) {
  return (
    <div>
      <p className="text-text-muted text-xs font-medium uppercase tracking-wider mb-2">Ordenar por</p>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-surface-2 border border-border text-text text-sm rounded-lg px-3 py-2
                   focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer"
      >
        {SORT_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}
