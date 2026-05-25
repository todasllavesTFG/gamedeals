const STORES = {
  steam:     { bg: '#1b2838', text: '#c7d5e0', label: 'S' },
  epic:      { bg: '#2d2d2d', text: '#ffffff', label: 'E' },
  gog:       { bg: '#7b4fa0', text: '#ffffff', label: 'G' },
  humble:    { bg: '#cc4e00', text: '#ffffff', label: 'H' },
  fanatical: { bg: '#cc0000', text: '#ffffff', label: 'F' },
};

export default function StoreIcon({ storeName = '' }) {
  const key = storeName.toLowerCase().replace(/\s+/g, '');
  const match = Object.keys(STORES).find((k) => key.includes(k));
  const { bg, text, label } = match
    ? STORES[match]
    : { bg: '#2a2a3d', text: '#e8e8f0', label: storeName.charAt(0).toUpperCase() || '?' };

  return (
    <span
      className="inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold flex-shrink-0"
      style={{ backgroundColor: bg, color: text }}
      title={storeName}
    >
      {label}
    </span>
  );
}
