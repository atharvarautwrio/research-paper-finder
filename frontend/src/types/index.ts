export type RetrievalMode = 'hybrid' | 'bm25' | 'tfidf' | 'semantic';
export type SortOption = 'relevance' | 'newest' | 'oldest' | 'citations';

export interface RankingWeights {
  bm25: number;
  tfidf: number;
  semantic: number;
  title_match: number;
  recency: number;
  citations: number;
}

export interface SearchFilter {
  categories?: string[];
  min_year?: number;
  max_year?: number;
  min_citations?: number;
  max_citations?: number;
  venues?: string[];
  authors?: string[];
}

export interface SearchRequest {
  query: string;
  mode: RetrievalMode;
  filters?: SearchFilter;
  sort_by: SortOption;
  page: number;
  page_size: number;
  weights?: RankingWeights;
}

export interface MatchExplanation {
  relevance_score: number;
  relevance_percentage: number;
  signals: {
    bm25?: number;
    tfidf?: number;
    semantic?: number;
    title_match?: number;
    recency?: number;
    citations?: number;
    [key: string]: number | undefined;
  };
  matched_query_terms: string[];
  title_match_terms: string[];
  reasons: string[];
  query_expansion_used: string[];
}

export interface SearchResultItem {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  keywords: string[];
  categories: string[];
  primary_category: string;
  publication_year: number;
  venue: string;
  citation_count: number;
  doi?: string;
  url?: string;
  pdf_url?: string;
  rank: number;
  explanation: MatchExplanation;
}

export interface FacetItem {
  name: string;
  count: number;
}

export interface SearchFacets {
  categories: FacetItem[];
  venues: FacetItem[];
  years: FacetItem[];
  citation_ranges: FacetItem[];
}

export interface SearchResponse {
  query: string;
  retrieval_mode: RetrievalMode;
  total_results: number;
  page: number;
  page_size: number;
  total_pages: number;
  latency_ms: number;
  results: SearchResultItem[];
  facets: SearchFacets;
  query_tokens: string[];
  expanded_terms: string[];
}

export interface PaperDetail {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  keywords: string[];
  categories: string[];
  primary_category: string;
  publication_year: number;
  venue: string;
  citation_count: number;
  doi?: string;
  url?: string;
  pdf_url?: string;
}

export interface PaperRecommendation {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  publication_year: number;
  venue: string;
  citation_count: number;
  primary_category: string;
  similarity_score: number;
  similarity_percentage: number;
  reasons: string[];
  signal_breakdown: {
    semantic: number;
    tfidf: number;
    category: number;
    relations: number;
  };
}

export interface YearlyCount {
  year: number;
  count: number;
}

export interface CategoryCount {
  category: string;
  count: number;
  percentage: number;
}

export interface KeywordCount {
  keyword: string;
  count: number;
}

export interface VenueCount {
  venue: string;
  count: number;
}

export interface CitationDistribution {
  tier: string;
  count: number;
}

export interface AnalyticsOverview {
  total_papers: number;
  total_authors: number;
  total_venues: number;
  total_categories: number;
  avg_citations: number;
  max_citations: number;
  median_citations: number;
  year_range: [number, number];
  papers_by_year: YearlyCount[];
  papers_by_category: CategoryCount[];
  top_keywords: KeywordCount[];
  top_venues: VenueCount[];
  citation_distribution: CitationDistribution[];
}

export interface TopicCluster {
  topic_id: number;
  name: string;
  top_terms: string[];
  paper_count: number;
  sample_titles: string[];
}

export interface TrendItem {
  topic: string;
  trajectory: number[];
  years: number[];
  cagr: number;
  status: 'Emerging' | 'Accelerating' | 'Stable' | 'Declining';
  total_papers: number;
}

export interface MethodMetrics {
  method_name: string;
  precision_at_5: number;
  precision_at_10: number;
  recall_at_5: number;
  recall_at_10: number;
  recall_at_20: number;
  f1_score: number;
  map_score: number;
  mrr_score: number;
  ndcg_at_5: number;
  ndcg_at_10: number;
  avg_latency_ms: number;
}

export interface QueryEvaluationDetail {
  query: string;
  category: string;
  num_judgments: number;
  methods: {
    [method: string]: {
      'p@10': number;
      map: number;
      mrr: number;
      'ndcg@10': number;
      latency_ms: number;
    };
  };
}

export interface BenchmarkReport {
  num_queries: number;
  methods: MethodMetrics[];
  query_details: QueryEvaluationDetail[];
  best_overall_method: string;
  summary_analysis: string;
}

export interface SavedPaper {
  paper_id: string;
  title: string;
  authors: string[];
  publication_year: number;
  primary_category: string;
  venue: string;
  notes?: string;
  saved_at?: string;
}

export interface SearchHistoryEntry {
  id: number;
  query: string;
  retrieval_mode: string;
  filters_applied?: any;
  result_count: number;
  latency_ms: number;
  created_at: string;
}

export interface SystemStats {
  indexed_papers_count: number;
  vocabulary_size: number;
  total_postings_count: number;
  categories_count: number;
  venues_count: number;
  embedding_dimension: number;
  embeddings_matrix_shape: number[];
  memory_usage_mb: number;
  index_files: { [key: string]: string };
  system_status: string;
  uptime_seconds: number;
  cache_stats: {
    cache_hits: number;
    cache_misses: number;
    cached_items: number;
  };
}
