import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useDebounce } from '../../hooks/useDebounce';

export default function SearchBar() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [value, setValue] = useState(searchParams.get('q') || '');
  const debouncedValue = useDebounce(value, 300);

  useEffect(() => {
    const trimmed = debouncedValue.trim();
    if (trimmed) {
      navigate('/search?q=' + encodeURIComponent(trimmed));
    }
  }, [debouncedValue, navigate]);

  return (
    <div className="relative w-full max-w-md min-w-0">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Buscar juegos..."
        className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-2 border border-border
                   text-text placeholder-text-muted text-sm
                   focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent
                   transition-colors"
      />
    </div>
  );
}
