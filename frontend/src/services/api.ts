import type {
  SearchRequest,
  SearchResponse,
  PaperDetail,
  PaperRecommendation,
  AnalyticsOverview,
  TopicCluster,
  TrendItem,
  BenchmarkReport,
  SavedPaper,
  SearchHistoryEntry,
  SystemStats
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export class ApiService {
  private static async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Network request failed');
      let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
      try {
        const errorJson = JSON.parse(errorText);
        if (errorJson.detail) {
          errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        if (errorText) errorMessage = errorText;
      }
      throw new Error(errorMessage);
    }
    return response.json();
  }

  // Search
  static async search(request: SearchRequest): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return this.handleResponse<SearchResponse>(response);
  }

  static async autocomplete(query: string, limit = 8): Promise<{ text: string; type: string; count: number }[]> {
    if (!query.trim()) return [];
    const response = await fetch(`${API_BASE_URL}/search/autocomplete?q=${encodeURIComponent(query)}&limit=${limit}`);
    return this.handleResponse(response);
  }

  static async expandQuery(query: string): Promise<{ original_query: string; base_tokens: string[]; expanded_synonyms: string[]; exact_phrases: string[] }> {
    const response = await fetch(`${API_BASE_URL}/search/expand?query=${encodeURIComponent(query)}`, {
      method: 'POST'
    });
    return this.handleResponse(response);
  }

  // Papers
  static async getRecentPapers(limit = 12, category?: string): Promise<PaperDetail[]> {
    const url = category
      ? `${API_BASE_URL}/papers/recent?limit=${limit}&category=${encodeURIComponent(category)}`
      : `${API_BASE_URL}/papers/recent?limit=${limit}`;
    const response = await fetch(url);
    return this.handleResponse<PaperDetail[]>(response);
  }

  static async getPaper(paperId: string): Promise<PaperDetail> {
    const response = await fetch(`${API_BASE_URL}/papers/${encodeURIComponent(paperId)}`);
    return this.handleResponse<PaperDetail>(response);
  }

  static async getRecommendations(paperId: string, topK = 6): Promise<PaperRecommendation[]> {
    const response = await fetch(`${API_BASE_URL}/papers/${encodeURIComponent(paperId)}/recommendations?top_k=${topK}`);
    return this.handleResponse<PaperRecommendation[]>(response);
  }

  // Analytics
  static async getOverview(): Promise<AnalyticsOverview> {
    const response = await fetch(`${API_BASE_URL}/analytics/overview`);
    return this.handleResponse<AnalyticsOverview>(response);
  }

  static async getTopics(): Promise<TopicCluster[]> {
    const response = await fetch(`${API_BASE_URL}/analytics/topics`);
    return this.handleResponse<TopicCluster[]>(response);
  }

  static async getTrends(): Promise<TrendItem[]> {
    const response = await fetch(`${API_BASE_URL}/analytics/trends`);
    return this.handleResponse<TrendItem[]>(response);
  }

  // Evaluation Benchmark
  static async getBenchmark(forceRerun = false): Promise<BenchmarkReport> {
    const response = await fetch(`${API_BASE_URL}/evaluation/benchmark?force_rerun=${forceRerun}`);
    return this.handleResponse<BenchmarkReport>(response);
  }

  static async getBenchmarkQueries(): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/evaluation/queries`);
    return this.handleResponse(response);
  }

  // History & Bookmarks
  static async getSearchHistory(limit = 25): Promise<SearchHistoryEntry[]> {
    const response = await fetch(`${API_BASE_URL}/history/searches?limit=${limit}`);
    return this.handleResponse<SearchHistoryEntry[]>(response);
  }

  static async getSavedPapers(): Promise<SavedPaper[]> {
    const response = await fetch(`${API_BASE_URL}/history/saved`);
    return this.handleResponse<SavedPaper[]>(response);
  }

  static async savePaper(paperId: string, notes?: string): Promise<{ status: string; paper_id: string }> {
    const response = await fetch(`${API_BASE_URL}/history/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ paper_id: paperId, notes })
    });
    return this.handleResponse(response);
  }

  static async removeSavedPaper(paperId: string): Promise<{ status: string; paper_id: string }> {
    const response = await fetch(`${API_BASE_URL}/history/saved/${encodeURIComponent(paperId)}`, {
      method: 'DELETE'
    });
    return this.handleResponse(response);
  }

  // System Diagnostics
  static async getSystemStats(): Promise<SystemStats> {
    const response = await fetch(`${API_BASE_URL}/system/stats`);
    return this.handleResponse<SystemStats>(response);
  }

  static async triggerReindex(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/system/reindex`, {
      method: 'POST'
    });
    return this.handleResponse(response);
  }
}
