const PLATFORMS = ['PC', 'PS5', 'Xbox', 'Switch'];

export default function PlatformFilter({ value = [], onChange }) {
  const toggle = (platform) => {
    const next = value.includes(platform)
      ? value.filter((p) => p !== platform)
      : [...value, platform];
    onChange(next);
  };

  return (
    <div>
      <p className="text-text-muted text-xs font-medium uppercase tracking-wider mb-2">Plataforma</p>
      <div className="flex flex-wrap gap-2">
        {PLATFORMS.map((p) => (
          <button
            key={p}
            onClick={() => toggle(p)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors cursor-pointer ${
              value.includes(p)
                ? 'bg-accent text-bg'
                : 'bg-surface-2 text-text-muted hover:text-text border border-border'
            }`}
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}
