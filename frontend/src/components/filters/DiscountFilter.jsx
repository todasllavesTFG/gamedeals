export default function DiscountFilter({ value = 0, onChange }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="text-text-muted text-xs font-medium uppercase tracking-wider">Descuento mínimo</p>
        <span className="text-accent text-xs font-bold">{value}%</span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        step="5"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 rounded-full appearance-none bg-surface-2 cursor-pointer
                   [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
                   [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                   [&::-webkit-slider-thumb]:bg-accent"
        style={{
          background: `linear-gradient(to right, var(--color-accent) ${value}%, var(--color-surface-2) ${value}%)`,
        }}
      />
    </div>
  );
}
