// Book types
export interface BookSummary {
  id: number;
  name: string;
  hebrew_name: string;
  order: number;
  total_chapters: number;
}

export interface ChapterSummary {
  number: number;
  total_verses: number;
}

export interface BookDetail extends BookSummary {
  chapters: ChapterSummary[];
}

export interface VerseResponse {
  id: number;
  ref: string;
  he_ref: string;
  text_hebrew: string;
  text_english: string;
  chapter: number;
  verse: number;
  processed: boolean;
  word_count: number | null;
  gematria_standard_total: number | null;
  gematria_katan_total: number | null;
}

export interface ChapterResponse {
  book: string;
  chapter: number;
  total_verses: number;
  verses: VerseResponse[];
}

// Name types
export type NameType = 'person' | 'deity' | 'place' | 'people_group' | 'angel' | 'unknown';

export interface NameSummary {
  id: number;
  name: string;
  hebrew: string | null;
  type: NameType;
  occurrences: number;
  first_mention: string | null;
}

export interface VerseOccurrence {
  ref: string;
  text: string;
  hebrew: string;
  surface_form: string;
}

export interface NameDetail {
  id: number;
  name: string;
  hebrew: string | null;
  type: NameType;
  first_mention: string | null;
  description: string | null;
  occurrences: number;
  verses: VerseOccurrence[];
}

export interface TimelineEntry {
  ref: string;
  book: string;
  chapter: number;
  verse: number;
  surface_form: string;
}

export interface NameTimeline {
  name: string;
  hebrew: string | null;
  total_occurrences: number;
  by_book: Record<string, number>;
  timeline: TimelineEntry[];
}

export interface CoOccurrence {
  name: string;
  hebrew: string | null;
  type: NameType;
  count: number;
}

export interface CoOccurrenceResponse {
  name: string;
  co_occurrences: CoOccurrence[];
}

export interface NearbyName {
  name: string;
  hebrew: string | null;
  type: NameType;
  count: number;
  avg_distance: number;
}

// Gematria types
export interface GematriaCalculation {
  text: string;
  standard: number;
  katan: number;
  ordinal: number;
  atbash: number;
}

export type GematriaMethod = 'standard' | 'katan' | 'ordinal' | 'atbash';

export interface WordMatch {
  word: string;
  word_normalized: string;
  verse_ref: string;
  position: number;
  gematria: number;
  verse_text_hebrew: string;
  verse_text_english: string;
}

export interface VerseMatch {
  ref: string;
  text_hebrew: string;
  text_english: string;
  gematria: number;
  word_count: number;
}

export interface GematriaStats {
  book: string | null;
  total_words: number;
  verses_populated: number;
  total_verses: number;
  population_percent: number;
  top_values: Array<{ value: number; count: number }>;
}

// Stats types
export interface GlobalStats {
  book: string | null;
  books: number;
  chapters: number;
  verses: number;
  processed: number;
  progress_percent: number;
  unique_names: number;
  total_occurrences: number;
  type_distribution: Record<NameType, number>;
}

export interface NamePair {
  name1: string;
  name2: string;
  count: number;
}

export interface GraphNode {
  id: string;
  label: string;
  hebrew: string | null;
  type: NameType;
  occurrences: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// Admin types
export interface ImportStatus {
  books: number;
  chapters: number;
  verses: number;
  expected_books: number;
}

export interface ExtractionStatus {
  total_verses: number;
  processed: number;
  pending: number;
  with_errors: number;
  unique_names: number;
  total_occurrences: number;
  progress_percent: number;
}

export interface GematriaPopulationStatus {
  total_verses: number;
  verses_populated: number;
  pending: number;
  total_words: number;
  progress_percent: number;
}

export interface BackgroundTaskResponse {
  status: string;
  message: string;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
