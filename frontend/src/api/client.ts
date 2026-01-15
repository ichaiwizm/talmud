import axios from 'axios';
import type {
  BookSummary,
  BookDetail,
  ChapterResponse,
  VerseResponse,
  NameSummary,
  NameDetail,
  NameTimeline,
  CoOccurrenceResponse,
  NearbyName,
  GematriaCalculation,
  GematriaMethod,
  WordMatch,
  VerseMatch,
  GematriaStats,
  GlobalStats,
  NamePair,
  GraphResponse,
  ImportStatus,
  ExtractionStatus,
  GematriaPopulationStatus,
  BackgroundTaskResponse,
  PaginatedResponse,
  NameType,
} from './types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Books API
export const booksApi = {
  list: async (): Promise<BookSummary[]> => {
    const { data } = await api.get('/books');
    return data;
  },

  get: async (bookName: string): Promise<BookDetail> => {
    const { data } = await api.get(`/books/${encodeURIComponent(bookName)}`);
    return data;
  },

  getChapter: async (bookName: string, chapter: number): Promise<ChapterResponse> => {
    const { data } = await api.get(`/books/${encodeURIComponent(bookName)}/chapters/${chapter}`);
    return data;
  },

  getVerse: async (bookName: string, chapter: number, verse: number): Promise<VerseResponse> => {
    const { data } = await api.get(
      `/books/${encodeURIComponent(bookName)}/chapters/${chapter}/verses/${verse}`
    );
    return data;
  },

  getVerseByRef: async (ref: string): Promise<VerseResponse> => {
    const { data } = await api.get(`/books/verses/${encodeURIComponent(ref)}`);
    return data;
  },
};

// Names API
export interface NamesListParams {
  name_type?: NameType;
  book?: string;
  sort_by?: 'frequency' | 'alpha';
  limit?: number;
  offset?: number;
}

export const namesApi = {
  list: async (params?: NamesListParams): Promise<PaginatedResponse<NameSummary>> => {
    const { data } = await api.get('/names', { params });
    return data;
  },

  get: async (name: string): Promise<NameDetail> => {
    const { data } = await api.get(`/names/${encodeURIComponent(name)}`);
    return data;
  },

  getOccurrences: async (
    name: string,
    params?: { book?: string; limit?: number }
  ): Promise<VerseResponse[]> => {
    const { data } = await api.get(`/names/${encodeURIComponent(name)}/occurrences`, { params });
    return data;
  },

  getTimeline: async (name: string, limit?: number): Promise<NameTimeline> => {
    const { data } = await api.get(`/names/${encodeURIComponent(name)}/timeline`, {
      params: { limit },
    });
    return data;
  },

  getCoOccurrences: async (
    name: string,
    params?: { min_count?: number; limit?: number }
  ): Promise<CoOccurrenceResponse> => {
    const { data } = await api.get(`/names/${encodeURIComponent(name)}/co-occurrences`, { params });
    return data;
  },

  getNearby: async (
    name: string,
    params?: { radius?: number; limit?: number }
  ): Promise<NearbyName[]> => {
    const { data } = await api.get(`/names/${encodeURIComponent(name)}/nearby`, { params });
    return data;
  },
};

// Search API
export const searchApi = {
  names: async (params: {
    q: string;
    exact?: boolean;
    include_hebrew?: boolean;
    limit?: number;
  }): Promise<NameSummary[]> => {
    const { data } = await api.get('/search/names', { params });
    return data;
  },

  verses: async (params: {
    q: string;
    book?: string;
    hebrew?: boolean;
    limit?: number;
  }): Promise<VerseResponse[]> => {
    const { data } = await api.get('/search/verses', { params });
    return data;
  },
};

// Gematria API
export const gematriaApi = {
  calculate: async (text: string): Promise<GematriaCalculation> => {
    const { data } = await api.get('/gematria/calculate', { params: { text } });
    return data;
  },

  searchWords: async (params: {
    value: number;
    method?: GematriaMethod;
    book?: string;
    limit?: number;
  }): Promise<WordMatch[]> => {
    const { data } = await api.get('/gematria/words', { params });
    return data;
  },

  searchVerses: async (params: {
    value: number;
    method?: GematriaMethod;
    book?: string;
    limit?: number;
  }): Promise<VerseMatch[]> => {
    const { data } = await api.get('/gematria/verses', { params });
    return data;
  },

  match: async (params: {
    text: string;
    method?: GematriaMethod;
    search_type?: 'words' | 'verses';
    book?: string;
    limit?: number;
  }): Promise<WordMatch[] | VerseMatch[]> => {
    const { data } = await api.get('/gematria/match', { params });
    return data;
  },

  stats: async (book?: string): Promise<GematriaStats> => {
    const { data } = await api.get('/gematria/stats', { params: { book } });
    return data;
  },
};

// Stats API
export const statsApi = {
  global: async (): Promise<GlobalStats> => {
    const { data } = await api.get('/stats');
    return data;
  },

  byBook: async (bookName: string): Promise<GlobalStats> => {
    const { data } = await api.get(`/stats/by-book/${encodeURIComponent(bookName)}`);
    return data;
  },

  topNames: async (params?: {
    limit?: number;
    name_type?: NameType;
    book?: string;
  }): Promise<NameSummary[]> => {
    const { data } = await api.get('/stats/top-names', { params });
    return data;
  },

  pairs: async (params?: { limit?: number; name_type?: NameType }): Promise<NamePair[]> => {
    const { data } = await api.get('/stats/pairs', { params });
    return data;
  },

  graph: async (params?: { min_weight?: number; name_type?: NameType }): Promise<GraphResponse> => {
    const { data } = await api.get('/stats/graph', { params });
    return data;
  },
};

// Admin API
export const adminApi = {
  importStatus: async (): Promise<ImportStatus> => {
    const { data } = await api.get('/admin/import/status');
    return data;
  },

  importTorah: async (): Promise<BackgroundTaskResponse> => {
    const { data } = await api.post('/admin/import/torah');
    return data;
  },

  importBook: async (bookName: string): Promise<BackgroundTaskResponse> => {
    const { data } = await api.post(`/admin/import/book/${encodeURIComponent(bookName)}`);
    return data;
  },

  extractionStatus: async (): Promise<ExtractionStatus> => {
    const { data } = await api.get('/admin/extraction/status');
    return data;
  },

  startExtraction: async (params?: {
    limit?: number;
    batch_size?: number;
    parallel?: boolean;
    workers?: number;
  }): Promise<BackgroundTaskResponse> => {
    const { data } = await api.post('/admin/extraction/start', params);
    return data;
  },

  retryExtraction: async (): Promise<BackgroundTaskResponse> => {
    const { data } = await api.post('/admin/extraction/retry');
    return data;
  },

  gematriaStatus: async (): Promise<GematriaPopulationStatus> => {
    const { data } = await api.get('/admin/gematria/status');
    return data;
  },

  populateGematria: async (params?: {
    limit?: number;
    book?: string;
  }): Promise<BackgroundTaskResponse> => {
    const { data } = await api.post('/admin/gematria/populate', params);
    return data;
  },

  health: async (): Promise<{ status: string }> => {
    const { data } = await api.get('/admin/health');
    return data;
  },

  healthDb: async (): Promise<{ status: string; details: string }> => {
    const { data } = await api.get('/admin/health/db');
    return data;
  },
};

export default api;
