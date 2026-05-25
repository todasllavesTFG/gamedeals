import PlatformFilter from './PlatformFilter';
import GenreFilter from './GenreFilter';
import PriceRangeFilter from './PriceRangeFilter';
import DiscountFilter from './DiscountFilter';
import SortDropdown from './SortDropdown';

export default function FilterSidebar({ filters, onChange }) {
  const update = (key) => (val) => onChange({ ...filters, [key]: val });
  const updatePrice = ({ minPrice, maxPrice }) =>
    onChange({ ...filters, minPrice, maxPrice });

  return (
    <aside className="bg-surface rounded-xl p-4 border border-border sticky top-20 flex flex-col gap-5">
      <h3 className="font-display text-sm font-semibold text-text">Filtros</h3>

      <SortDropdown value={filters.sortBy} onChange={update('sortBy')} />
      <PlatformFilter value={filters.platforms} onChange={update('platforms')} />
      <GenreFilter value={filters.genre} onChange={update('genre')} />
      <PriceRangeFilter
        minPrice={filters.minPrice}
        maxPrice={filters.maxPrice}
        onChange={updatePrice}
      />
      <DiscountFilter value={filters.minDiscount} onChange={update('minDiscount')} />

      <button
        onClick={() =>
          onChange({
            platforms: [],
            genre: '',
            minPrice: undefined,
            maxPrice: undefined,
            minDiscount: 0,
            sortBy: 'discount',
          })
        }
        className="text-xs text-text-muted hover:text-danger transition-colors cursor-pointer text-left"
      >
        Limpiar filtros
      </button>
    </aside>
  );
}
