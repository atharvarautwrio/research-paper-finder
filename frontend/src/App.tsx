import { useState, useEffect } from 'react';
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import './App.css';

import type {
  RetrievalMode,
  SortOption,
  RankingWeights,
  SearchFilter,
  SearchResultItem,
  SearchResponse,
  SystemStats,
  SavedPaper
} from './types';
import { ApiService } from './services/api';

import { Navbar } from './components/Navbar';
import { SearchBar } from './components/SearchBar';
import { RetrievalModeSelector } from './components/RetrievalModeSelector';
import { WeightTuner } from './components/WeightTuner';
import { FilterSidebar } from './components/FilterSidebar';
import { PaperCard } from './components/PaperCard';
import { ExplainabilityModal } from './components/ExplainabilityModal';
import { PaperDetailModal } from './components/PaperDetailModal';
import { AnalyticsView } from './components/AnalyticsView';
import { BenchmarkView } from './components/BenchmarkView';
import { SavedPapersDrawer } from './components/SavedPapersDrawer';
import { SystemStatsModal } from './components/SystemStatsModal';

const DEFAULT_WEIGHTS: RankingWeights = {
  bm25: 0.35,
  tfidf: 0.15,
  semantic: 0.35,
  title_match: 0.10,
  recency: 0.03,
  citations: 0.02
};

export function App() {
  // Navigation & View state
  const [activeTab, setActiveTab] = useState<'search' | 'analytics' | 'benchmark' | 'saved'>('search');
  const [darkMode, setDarkMode] = useState(true);

  // Search parameters
  const [query, setQuery] = useState('');
  const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>('hybrid');
  const [weights, setWeights] = useState<RankingWeights>(DEFAULT_WEIGHTS);
  const [filters, setFilters] = useState<SearchFilter>({});
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // Search results state
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Modals & Selected Paper
  const [explainPaper, setExplainPaper] = useState<SearchResultItem | null>(null);
  const [selectedPaperId, setSelectedPaperId] = useState<string | null>(null);
  const [showStatsModal, setShowStatsModal] = useState(false);

  // Saved library & System status
  const [savedPapers, setSavedPapers] = useState<SavedPaper[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);

  // Initial load
  useEffect(() => {
    // Dark mode class on html
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const loadSavedPapers = async () => {
    try {
      const data = await ApiService.getSavedPapers();
      setSavedPapers(data);
    } catch (err) {
      console.error('Failed to load saved papers:', err);
    }
  };

  const loadSystemStats = async () => {
    try {
      const data = await ApiService.getSystemStats();
      setSystemStats(data);
    } catch (err) {
      console.error('Failed to load system stats:', err);
    }
  };

  useEffect(() => {
    loadSavedPapers();
    loadSystemStats();
    // Default search on first open
    executeSearch('attention transformers natural language processing', 1);
  }, []);

  const executeSearch = async (targetQuery?: string, targetPage = 1) => {
    const q = (targetQuery !== undefined ? targetQuery : query).trim();
    if (!q) return;

    setIsSearching(true);
    setSearchError(null);
    setPage(targetPage);

    try {
      const res = await ApiService.search({
        query: q,
        mode: retrievalMode,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
        sort_by: sortBy,
        page: targetPage,
        page_size: pageSize,
        weights: retrievalMode === 'hybrid' ? weights : undefined
      });
      setSearchResponse(res);
      loadSavedPapers();
    } catch (err: any) {
      console.error('Search failed:', err);
      setSearchError(err.message || 'Search failed to connect to backend.');
    } finally {
      setIsSearching(false);
    }
  };

  // Trigger search on mode, filter, or sort changes
  const handleModeChange = (mode: RetrievalMode) => {
    setRetrievalMode(mode);
  };

  useEffect(() => {
    if (query.trim() && searchResponse) {
      executeSearch(query, 1);
    }
  }, [retrievalMode, filters, sortBy]);

  const handleToggleSave = async (paperId: string) => {
    const isAlreadySaved = savedPapers.some((p) => p.paper_id === paperId);
    try {
      if (isAlreadySaved) {
        await ApiService.removeSavedPaper(paperId);
      } else {
        await ApiService.savePaper(paperId);
      }
      loadSavedPapers();
    } catch (err) {
      console.error('Failed to toggle save:', err);
    }
  };

  const handleTopicSearch = (topicName: string) => {
    setQuery(topicName);
    setActiveTab('search');
    executeSearch(topicName, 1);
  };

  const savedIdsSet = new Set(savedPapers.map((p) => p.paper_id));

  return (
    <div className={`app-root ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        savedCount={savedPapers.length}
        darkMode={darkMode}
        toggleDarkMode={() => setDarkMode(!darkMode)}
        systemStats={systemStats}
        onOpenStats={() => setShowStatsModal(true)}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {activeTab === 'search' && (
          <div className="search-view-layout">
            {/* Search Header Hero */}
            <div className="search-header-hero">
              <h1 className="main-heading">
                Explore <span className="gradient-text">30,000+ Academic Research Papers</span>
              </h1>
              <p className="sub-heading">
                Multi-stage hybrid information retrieval fusing Okapi BM25, TF-IDF, and 384-dimensional dense semantic vector embeddings.
              </p>

              {/* Search Bar with Autocomplete & Query Expansion */}
              <SearchBar
                query={query}
                setQuery={setQuery}
                onSearch={(q) => executeSearch(q, 1)}
                isLoading={isSearching}
                queryTokens={searchResponse?.query_tokens}
                expandedTerms={searchResponse?.expanded_terms}
              />

              {/* Retrieval Mode Selector */}
              <RetrievalModeSelector
                currentMode={retrievalMode}
                onChange={handleModeChange}
              />

              {/* Hybrid Weight Tuner (visible only in Hybrid mode) */}
              {retrievalMode === 'hybrid' && (
                <WeightTuner
                  weights={weights}
                  onChange={setWeights}
                  onApply={() => executeSearch(query, 1)}
                />
              )}
            </div>

            {/* Search Error Banner */}
            {searchError && (
              <div className="error-banner">
                <AlertCircle className="error-icon" />
                <div className="error-text">
                  <strong>Retrieval Engine Notice:</strong> {searchError}
                </div>
                <button
                  type="button"
                  className="retry-btn"
                  onClick={() => executeSearch(query, page)}
                >
                  <RefreshCw className="retry-icon" /> Retry
                </button>
              </div>
            )}

            {/* Results Layout Grid */}
            <div className="results-layout-grid">
              {/* Filter Sidebar */}
              <FilterSidebar
                facets={searchResponse?.facets || null}
                filters={filters}
                setFilters={setFilters}
                sortBy={sortBy}
                setSortBy={setSortBy}
                totalResults={searchResponse?.total_results || 0}
              />

              {/* Search Results Column */}
              <section className="results-column">
                {/* Result Meta Header */}
                {searchResponse && (
                  <div className="results-meta-bar">
                    <div className="meta-left">
                      <span className="results-count-text">
                        Found <strong>{searchResponse.total_results.toLocaleString()}</strong> results for{' '}
                        <em>"{searchResponse.query}"</em>
                      </span>
                      <span className="latency-badge">
                        ⏱ {searchResponse.latency_ms} ms ({searchResponse.retrieval_mode.toUpperCase()})
                      </span>
                    </div>

                    {searchResponse.total_pages > 1 && (
                      <div className="meta-right">
                        <span className="page-indicator">
                          Page {searchResponse.page} of {searchResponse.total_pages}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Loading State */}
                {isSearching ? (
                  <div className="results-loading-state">
                    <div className="spinner large"></div>
                    <p className="loading-text">
                      Retrieving & scoring candidates across BM25, TF-IDF, and dense vector indexes...
                    </p>
                  </div>
                ) : searchResponse && searchResponse.results.length > 0 ? (
                  <div className="papers-list">
                    {searchResponse.results.map((paper) => (
                      <PaperCard
                        key={paper.paper_id}
                        paper={paper}
                        onExplain={(p) => setExplainPaper(p)}
                        onViewDetails={(pid) => setSelectedPaperId(pid)}
                        onFindSimilar={(pid) => setSelectedPaperId(pid)}
                        isSaved={savedIdsSet.has(paper.paper_id)}
                        onToggleSave={handleToggleSave}
                      />
                    ))}

                    {/* Pagination */}
                    {searchResponse.total_pages > 1 && (
                      <div className="pagination-bar">
                        <button
                          type="button"
                          className="pagination-nav-btn"
                          disabled={page <= 1}
                          onClick={() => executeSearch(query, page - 1)}
                        >
                          <ChevronLeft className="icon" /> Previous
                        </button>

                        <div className="page-numbers">
                          {Array.from(
                            { length: Math.min(searchResponse.total_pages, 7) },
                            (_, i) => {
                              let pageNum = i + 1;
                              if (searchResponse.total_pages > 7 && page > 4) {
                                pageNum = page - 3 + i;
                                if (pageNum > searchResponse.total_pages) {
                                  pageNum = searchResponse.total_pages - (6 - i);
                                }
                              }
                              return (
                                <button
                                  key={pageNum}
                                  type="button"
                                  className={`page-num-btn ${page === pageNum ? 'active' : ''}`}
                                  onClick={() => executeSearch(query, pageNum)}
                                >
                                  {pageNum}
                                </button>
                              );
                            }
                          )}
                        </div>

                        <button
                          type="button"
                          className="pagination-nav-btn"
                          disabled={page >= searchResponse.total_pages}
                          onClick={() => executeSearch(query, page + 1)}
                        >
                          Next <ChevronRight className="icon" />
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  !isSearching && (
                    <div className="no-results-box">
                      <BookOpen className="no-results-icon" />
                      <h3>No Matching Research Papers Found</h3>
                      <p>
                        Try broadening your search query, clearing active filters, or switching to <strong>Dense Semantic</strong> retrieval mode.
                      </p>
                    </div>
                  )
                )}
              </section>
            </div>
          </div>
        )}

        {/* Analytics & Trends View */}
        {activeTab === 'analytics' && (
          <AnalyticsView onSearchTopic={handleTopicSearch} />
        )}

        {/* IR Benchmark Evaluation View */}
        {activeTab === 'benchmark' && <BenchmarkView />}

        {/* Saved Papers Library View */}
        {activeTab === 'saved' && (
          <SavedPapersDrawer
            savedPapers={savedPapers}
            onRemovePaper={handleToggleSave}
            onViewDetails={(pid) => setSelectedPaperId(pid)}
            onRefresh={loadSavedPapers}
          />
        )}
      </main>

      {/* Explainability Scoring Breakdown Modal */}
      {explainPaper && (
        <ExplainabilityModal
          paper={explainPaper}
          onClose={() => setExplainPaper(null)}
          query={query}
        />
      )}

      {/* Paper Details & Recommendation Drawer Modal */}
      {selectedPaperId && (
        <PaperDetailModal
          paperId={selectedPaperId}
          onClose={() => setSelectedPaperId(null)}
          onSelectPaper={(pid) => setSelectedPaperId(pid)}
          isSaved={savedIdsSet.has(selectedPaperId)}
          onToggleSave={handleToggleSave}
        />
      )}

      {/* System Stats & Diagnostics Modal */}
      {showStatsModal && (
        <SystemStatsModal
          stats={systemStats}
          onClose={() => setShowStatsModal(false)}
          onRefresh={loadSystemStats}
        />
      )}
    </div>
  );
}

export default App;
