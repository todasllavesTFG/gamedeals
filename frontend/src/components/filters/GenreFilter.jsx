const GENRES = ['', 'RPG', 'Acción', 'Aventura', 'Estrategia', 'Plataformas', 'Indie', 'Shooter'];

export default function GenreFilter({ value = '', onChange }) {
  return (
    <div>
      <p className="text-text-muted text-xs font-medium uppercase tracking-wider mb-2">Género</p>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-surface-2 border border-border text-text text-sm rounded-lg px-3 py-2
                   focus:outline-none focus:ring-2 focus:ring-accent/50 cursor-pointer"
      >
        <option value="">Todos los géneros</option>
        {GENRES.filter(Boolean).map((g) => (
          <option key={g} value={g}>{g}</option>
        ))}
      </select>
    </div>
  );
}
