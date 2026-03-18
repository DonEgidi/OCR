import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { SearchFilters } from '../types';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (filters: SearchFilters) => void;
  filters: SearchFilters;
}

const SearchBar = ({ onSearch, filters }: SearchBarProps) => {
  const [localFilters, setLocalFilters] = useState<SearchFilters>(filters);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(localFilters);
  };

  const handleChange = (field: keyof SearchFilters, value: string) => {
    setLocalFilters({ ...localFilters, [field]: value });
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Buscar archivos..."
            value={localFilters.query}
            onChange={(e) => handleChange('query', e.target.value)}
            className="search-input"
          />
          <button
            type="button"
            className="filter-toggle"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            <Filter size={18} />
            Filtros
          </button>
          <button type="submit" className="search-button">
            Buscar
          </button>
        </div>

        {showAdvanced && (
          <div className="advanced-filters">
            <div className="filter-group">
              <label>Extensión</label>
              <input
                type="text"
                placeholder="pdf, txt, jpg..."
                value={localFilters.extension}
                onChange={(e) => handleChange('extension', e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Tamaño mínimo (MB)</label>
              <input
                type="number"
                placeholder="0"
                value={localFilters.minSize}
                onChange={(e) => handleChange('minSize', e.target.value)}
              />
            </div>

            <div className="filter-group">
              <label>Tamaño máximo (MB)</label>
              <input
                type="number"
                placeholder="100"
                value={localFilters.maxSize}
                onChange={(e) => handleChange('maxSize', e.target.value)}
              />
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default SearchBar;
