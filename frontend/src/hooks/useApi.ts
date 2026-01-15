import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  booksApi,
  namesApi,
  searchApi,
  gematriaApi,
  statsApi,
  adminApi,
  type NamesListParams,
} from '../api/client';
import type { NameType, GematriaMethod } from '../api/types';

// Books hooks
export const useBooks = () =>
  useQuery({
    queryKey: ['books'],
    queryFn: booksApi.list,
  });

export const useBook = (bookName: string) =>
  useQuery({
    queryKey: ['book', bookName],
    queryFn: () => booksApi.get(bookName),
    enabled: !!bookName,
  });

export const useChapter = (bookName: string, chapter: number) =>
  useQuery({
    queryKey: ['chapter', bookName, chapter],
    queryFn: () => booksApi.getChapter(bookName, chapter),
    enabled: !!bookName && chapter > 0,
  });

export const useVerse = (bookName: string, chapter: number, verse: number) =>
  useQuery({
    queryKey: ['verse', bookName, chapter, verse],
    queryFn: () => booksApi.getVerse(bookName, chapter, verse),
    enabled: !!bookName && chapter > 0 && verse > 0,
  });

// Names hooks
export const useNames = (params?: NamesListParams) =>
  useQuery({
    queryKey: ['names', params],
    queryFn: () => namesApi.list(params),
    placeholderData: (prev) => prev,
  });

export const useName = (name: string) =>
  useQuery({
    queryKey: ['name', name],
    queryFn: () => namesApi.get(name),
    enabled: !!name,
  });

export const useNameOccurrences = (name: string, params?: { book?: string; limit?: number }) =>
  useQuery({
    queryKey: ['name-occurrences', name, params],
    queryFn: () => namesApi.getOccurrences(name, params),
    enabled: !!name,
  });

export const useNameTimeline = (name: string, limit?: number) =>
  useQuery({
    queryKey: ['name-timeline', name, limit],
    queryFn: () => namesApi.getTimeline(name, limit),
    enabled: !!name,
  });

export const useNameCoOccurrences = (
  name: string,
  params?: { min_count?: number; limit?: number }
) =>
  useQuery({
    queryKey: ['name-co-occurrences', name, params],
    queryFn: () => namesApi.getCoOccurrences(name, params),
    enabled: !!name,
  });

export const useNameNearby = (name: string, params?: { radius?: number; limit?: number }) =>
  useQuery({
    queryKey: ['name-nearby', name, params],
    queryFn: () => namesApi.getNearby(name, params),
    enabled: !!name,
  });

// Search hooks
export const useSearchNames = (
  q: string,
  options?: { exact?: boolean; include_hebrew?: boolean; limit?: number }
) =>
  useQuery({
    queryKey: ['search-names', q, options],
    queryFn: () => searchApi.names({ q, ...options }),
    enabled: q.length > 0,
  });

export const useSearchVerses = (
  q: string,
  options?: { book?: string; hebrew?: boolean; limit?: number }
) =>
  useQuery({
    queryKey: ['search-verses', q, options],
    queryFn: () => searchApi.verses({ q, ...options }),
    enabled: q.length > 0,
  });

// Gematria hooks
export const useGematriaCalculate = (text: string) =>
  useQuery({
    queryKey: ['gematria-calculate', text],
    queryFn: () => gematriaApi.calculate(text),
    enabled: text.length > 0,
  });

export const useGematriaWords = (
  value: number,
  options?: { method?: GematriaMethod; book?: string; limit?: number }
) =>
  useQuery({
    queryKey: ['gematria-words', value, options],
    queryFn: () => gematriaApi.searchWords({ value, ...options }),
    enabled: value > 0,
  });

export const useGematriaVerses = (
  value: number,
  options?: { method?: GematriaMethod; book?: string; limit?: number }
) =>
  useQuery({
    queryKey: ['gematria-verses', value, options],
    queryFn: () => gematriaApi.searchVerses({ value, ...options }),
    enabled: value > 0,
  });

export const useGematriaStats = (book?: string) =>
  useQuery({
    queryKey: ['gematria-stats', book],
    queryFn: () => gematriaApi.stats(book),
  });

// Stats hooks
export const useGlobalStats = () =>
  useQuery({
    queryKey: ['global-stats'],
    queryFn: statsApi.global,
  });

export const useBookStats = (bookName: string) =>
  useQuery({
    queryKey: ['book-stats', bookName],
    queryFn: () => statsApi.byBook(bookName),
    enabled: !!bookName,
  });

export const useTopNames = (params?: { limit?: number; name_type?: NameType; book?: string }) =>
  useQuery({
    queryKey: ['top-names', params],
    queryFn: () => statsApi.topNames(params),
  });

export const useNamePairs = (params?: { limit?: number; name_type?: NameType }) =>
  useQuery({
    queryKey: ['name-pairs', params],
    queryFn: () => statsApi.pairs(params),
  });

export const useGraph = (params?: { min_weight?: number; name_type?: NameType }) =>
  useQuery({
    queryKey: ['graph', params],
    queryFn: () => statsApi.graph(params),
  });

// Admin hooks
export const useImportStatus = () =>
  useQuery({
    queryKey: ['admin', 'import-status'],
    queryFn: adminApi.importStatus,
  });

export const useExtractionStatus = () =>
  useQuery({
    queryKey: ['admin', 'extraction-status'],
    queryFn: adminApi.extractionStatus,
  });

export const useGematriaPopulationStatus = () =>
  useQuery({
    queryKey: ['admin', 'gematria-status'],
    queryFn: adminApi.gematriaStatus,
  });

export const useHealth = () =>
  useQuery({
    queryKey: ['admin', 'health'],
    queryFn: adminApi.health,
    refetchInterval: 30000,
  });

// Admin mutations
export const useImportTorah = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.importTorah,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'import-status'] });
    },
  });
};

export const useStartExtraction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.startExtraction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'extraction-status'] });
    },
  });
};

export const usePopulateGematria = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminApi.populateGematria,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'gematria-status'] });
    },
  });
};
