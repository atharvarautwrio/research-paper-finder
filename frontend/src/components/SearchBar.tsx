import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Sparkles, CornerDownLeft, Tag, Layers } from 'lucide-react';
import { ApiService } from '../services/api';

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (q?: string) => void;
  isLoading: boolean;
  queryTokens?: string[];
  expandedTerms?: string[];
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  setQuery,
  onSearch,
  isLoading,
  queryTokens = [],
  expandedTerms = []
}) => {
  const [suggestions, setSuggestions] = useState<{ text: string; type: string; count: number }[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.trim().length >= 2) {
        try {
          const res = await ApiService.autocomplete(query, 6);
          setSuggestions(res);
          setShowDropdown(res.length > 0);
        } catch {
          setSuggestions([]);
          setShowDropdown(false);
        }
      } else {
        setSuggestions([]);
        setShowDropdown(false);
      }
    };

    const timeout = setTimeout(fetchSuggestions, 180);
    return () => clearTimeout(timeout);
  }, [query]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIdx((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIdx((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIdx >= 0 && selectedIdx < suggestions.length) {
        const item = suggestions[selectedIdx];
        setQuery(item.text);
        setShowDropdown(false);
        onSearch(item.text);
      } else {
        setShowDropdown(false);
        onSearch();
      }
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleSelectSuggestion = (item: { text: string }) => {
    setQuery(item.text);
    setShowDropdown(false);
    onSearch(item.text);
  };

  const SAMPLE_QUERIES = [
    'Attention and Transformers in NLP',
    'Spring Boot microservices architecture',
    'Prospect Theory decision under risk',
    'SQL query optimization and indexing',
    'CRISPR Cas9 gene editing mechanisms',
    'Kubernetes container pod autoscaling',
    'Deep learning for medical MRI segmentation',
    'Observation of Gravitational Waves LIGO',
    'BM25 and hybrid neural ranking algorithms'
  ];

  return (
    <div className="search-bar-wrapper" ref={dropdownRef}>
      <form
        className="search-input-form"
        onSubmit={(e) => {
          e.preventDefault();
          setShowDropdown(false);
          onSearch();
        }}
      >
        <div className="search-input-container">
          <Search className="search-leading-icon" />
          <input
            ref={inputRef}
            type="text"
            className="main-search-input"
            placeholder="Search 30,000+ papers by title, abstract, keywords, author, or research problem..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIdx(-1);
            }}
            onFocus={() => {
              if (suggestions.length > 0) setShowDropdown(true);
            }}
            onKeyDown={handleKeyDown}
          />

          {query && (
            <button
              type="button"
              className="clear-query-btn"
              onClick={() => {
                setQuery('');
                setSuggestions([]);
                setShowDropdown(false);
                inputRef.current?.focus();
              }}
              title="Clear search"
            >
              <X className="clear-icon" />
            </button>
          )}

          <button
            type="submit"
            className={`submit-search-btn ${isLoading ? 'loading' : ''}`}
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? (
              <span className="spinner"></span>
            ) : (
              <>
                <span>Search Papers</span>
                <CornerDownLeft className="enter-key-icon" />
              </>
            )}
          </button>
        </div>

        {/* Autocomplete Dropdown */}
        {showDropdown && suggestions.length > 0 && (
          <div className="autocomplete-dropdown">
            <div className="dropdown-header">
              <span>Suggested terms & topics</span>
            </div>
            {suggestions.map((item, idx) => (
              <div
                key={idx}
                className={`autocomplete-item ${idx === selectedIdx ? 'selected' : ''}`}
                onClick={() => handleSelectSuggestion(item)}
              >
                <div className="item-left">
                  {item.type === 'topic' ? (
                    <Layers className="item-icon topic-icon" />
                  ) : (
                    <Tag className="item-icon tag-icon" />
                  )}
                  <span className="item-text">{item.text}</span>
                </div>
                <span className="item-count">
                  {item.count ? `${item.count} papers` : item.type}
                </span>
              </div>
            ))}
          </div>
        )}
      </form>

      {/* Query Expansion & Synonyms Badges */}
      {(queryTokens.length > 0 || expandedTerms.length > 0) && (
        <div className="query-expansion-bar">
          <div className="expansion-title">
            <Sparkles className="sparkle-icon" />
            <span>Query Analysis:</span>
          </div>
          <div className="expansion-pills">
            {queryTokens.map((token, i) => (
              <span key={`tok-${i}`} className="token-pill base-token" title="Stemmed root term">
                {token}
              </span>
            ))}
            {expandedTerms.map((term, i) => (
              <span key={`exp-${i}`} className="token-pill expanded-synonym" title="Expanded domain synonym">
                + {term}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Quick Search Starters when no active search */}
      {!query && (
        <div className="quick-starters">
          <span className="starters-label">Try searching:</span>
          <div className="starters-chips">
            {SAMPLE_QUERIES.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className="starter-chip"
                onClick={() => {
                  setQuery(sample);
                  onSearch(sample);
                }}
              >
                {sample}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
