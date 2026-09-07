import React from 'react';
import { Filter, RotateCcw, Calendar, BookOpen, Award, BarChart3, ArrowUpDown } from 'lucide-react';
import type { SearchFilter, SearchFacets, SortOption } from '../types';

interface FilterSidebarProps {
  facets: SearchFacets | null;
  filters: SearchFilter;
  setFilters: React.Dispatch<React.SetStateAction<SearchFilter>>;
  sortBy: SortOption;
  setSortBy: (sort: SortOption) => void;
  totalResults: number;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({
  facets,
  filters,
  setFilters,
  sortBy,
  setSortBy,
  totalResults
}) => {
  const selectedCategories = filters.categories || [];
  const selectedVenues = filters.venues || [];

  const handleCategoryToggle = (category: string) => {
    const updated = selectedCategories.includes(category)
      ? selectedCategories.filter((c) => c !== category)
      : [...selectedCategories, category];

    setFilters((prev) => ({
      ...prev,
      categories: updated.length > 0 ? updated : undefined
    }));
  };

  const handleVenueToggle = (venue: string) => {
    const updated = selectedVenues.includes(venue)
      ? selectedVenues.filter((v) => v !== venue)
      : [...selectedVenues, venue];

    setFilters((prev) => ({
      ...prev,
      venues: updated.length > 0 ? updated : undefined
    }));
  };

  const handleYearSelect = (min?: number, max?: number) => {
    setFilters((prev) => ({
      ...prev,
      min_year: min,
      max_year: max
    }));
  };

  const handleCitationTierSelect = (min?: number, max?: number) => {
    setFilters((prev) => ({
      ...prev,
      min_citations: min,
      max_citations: max
    }));
  };

  const handleReset = () => {
    setFilters({});
    setSortBy('relevance');
  };

  const hasActiveFilters =
    (filters.categories && filters.categories.length > 0) ||
    (filters.venues && filters.venues.length > 0) ||
    filters.min_year !== undefined ||
    filters.max_year !== undefined ||
    filters.min_citations !== undefined ||
    sortBy !== 'relevance';

  return (
    <aside className="filter-sidebar">
      {/* Header */}
      <div className="filter-header">
        <div className="filter-title-group">
          <Filter className="filter-icon" />
          <span className="filter-title">Filter & Refine</span>
          <span className="result-counter">{totalResults.toLocaleString()} papers</span>
        </div>
        {hasActiveFilters && (
          <button type="button" className="reset-filter-btn" onClick={handleReset}>
            <RotateCcw className="reset-icon" /> Reset
          </button>
        )}
      </div>

      {/* Sorting */}
      <div className="filter-section">
        <label className="section-label">
          <ArrowUpDown className="section-icon" /> Sort Order
        </label>
        <select
          className="custom-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortOption)}
        >
          <option value="relevance">Relevance (Hybrid Score)</option>
          <option value="newest">Newest First (2025 - 2017)</option>
          <option value="oldest">Oldest First</option>
          <option value="citations">Most Cited First</option>
        </select>
      </div>

      {/* Categories Facet */}
      {facets && facets.categories && facets.categories.length > 0 && (
        <div className="filter-section">
          <label className="section-label">
            <BookOpen className="section-icon" /> Research Domain
          </label>
          <div className="facet-list">
            {facets.categories.map((cat) => {
              const isChecked = selectedCategories.includes(cat.name);
              return (
                <label key={cat.name} className={`facet-checkbox-label ${isChecked ? 'selected' : ''}`}>
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => handleCategoryToggle(cat.name)}
                    className="facet-checkbox"
                  />
                  <span className="facet-name">{cat.name}</span>
                  <span className="facet-count">{cat.count.toLocaleString()}</span>
                </label>
              );
            })}
          </div>
        </div>
      )}

      {/* Publication Year Ranges */}
      <div className="filter-section">
        <label className="section-label">
          <Calendar className="section-icon" /> Publication Era
        </label>
        <div className="year-pills-grid">
          <button
            type="button"
            className={`year-pill ${filters.min_year === 2024 ? 'active' : ''}`}
            onClick={() => handleYearSelect(2024, undefined)}
          >
            2024 - 2025
          </button>
          <button
            type="button"
            className={`year-pill ${filters.min_year === 2022 && filters.max_year === 2023 ? 'active' : ''}`}
            onClick={() => handleYearSelect(2022, 2023)}
          >
            2022 - 2023
          </button>
          <button
            type="button"
            className={`year-pill ${filters.min_year === 2020 && filters.max_year === 2021 ? 'active' : ''}`}
            onClick={() => handleYearSelect(2020, 2021)}
          >
            2020 - 2021
          </button>
          <button
            type="button"
            className={`year-pill ${filters.max_year === 2019 ? 'active' : ''}`}
            onClick={() => handleYearSelect(undefined, 2019)}
          >
            2017 - 2019
          </button>
        </div>
      </div>

      {/* Citation Impact Tiers */}
      <div className="filter-section">
        <label className="section-label">
          <Award className="section-icon" /> Citation Impact
        </label>
        <div className="cit-tiers-list">
          <button
            type="button"
            className={`cit-tier-btn ${filters.min_citations === 1000 ? 'active' : ''}`}
            onClick={() => handleCitationTierSelect(1000, undefined)}
          >
            <span>Foundational (1,000+ citations)</span>
          </button>
          <button
            type="button"
            className={`cit-tier-btn ${filters.min_citations === 100 && filters.max_citations === 1000 ? 'active' : ''}`}
            onClick={() => handleCitationTierSelect(100, 1000)}
          >
            <span>High Impact (100 - 1,000)</span>
          </button>
          <button
            type="button"
            className={`cit-tier-btn ${filters.min_citations === 10 && filters.max_citations === 100 ? 'active' : ''}`}
            onClick={() => handleCitationTierSelect(10, 100)}
          >
            <span>Growing (10 - 100)</span>
          </button>
        </div>
      </div>

      {/* Venues Facet */}
      {facets && facets.venues && facets.venues.length > 0 && (
        <div className="filter-section">
          <label className="section-label">
            <BarChart3 className="section-icon" /> Conferences & Journals
          </label>
          <div className="facet-list scrollable">
            {facets.venues.slice(0, 8).map((ven) => {
              const isChecked = selectedVenues.includes(ven.name);
              return (
                <label key={ven.name} className={`facet-checkbox-label ${isChecked ? 'selected' : ''}`}>
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => handleVenueToggle(ven.name)}
                    className="facet-checkbox"
                  />
                  <span className="facet-name">{ven.name}</span>
                  <span className="facet-count">{ven.count}</span>
                </label>
              );
            })}
          </div>
        </div>
      )}
    </aside>
  );
};
