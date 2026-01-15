import { useState } from 'react';
import { Search as SearchIcon, Users, FileText } from 'lucide-react';
import { useSearchNames, useSearchVerses } from '../hooks/useApi';
import { useUIStore } from '../store';
import { NameBadge } from '../components/domain/NameBadge';
import { VerseCard } from '../components/domain/VerseCard';
import { Card } from '../components/ui/Card';
import { Input, Select, Tabs, TabsList, TabsTrigger } from '../components/ui';
import { Skeleton } from '../components/ui/Loading';
import { TORAH_BOOKS, formatNumber } from '../lib/utils';
import { useDebounce } from '../hooks/useDebounce';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'names' | 'verses'>('names');
  const [includeHebrew, setIncludeHebrew] = useState(false);
  const [exactMatch, setExactMatch] = useState(false);
  const [bookFilter, setBookFilter] = useState('');

  const { recentSearches, addRecentSearch, clearRecentSearches } = useUIStore();

  const debouncedQuery = useDebounce(query, 300);

  const { data: nameResults, isLoading: namesLoading } = useSearchNames(
    searchType === 'names' ? debouncedQuery : '',
    { exact: exactMatch, include_hebrew: includeHebrew, limit: 50 }
  );

  const { data: verseResults, isLoading: versesLoading } = useSearchVerses(
    searchType === 'verses' ? debouncedQuery : '',
    { book: bookFilter || undefined, hebrew: includeHebrew, limit: 50 }
  );

  const handleSearch = (q: string) => {
    setQuery(q);
    if (q.length > 2) {
      addRecentSearch(q);
    }
  };

  const isLoading = searchType === 'names' ? namesLoading : versesLoading;
  const hasResults = searchType === 'names' ? nameResults?.length : verseResults?.length;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <SearchIcon className="w-8 h-8 text-gold-500" />
          <h1 className="display-heading text-3xl text-parchment-50">Search</h1>
        </div>
        <p className="text-parchment-200/60">
          Search for names or verses in the Torah
        </p>
      </div>

      {/* Search input */}
      <Card variant="bordered" className="p-6 mb-6">
        <div className="space-y-4">
          <Input
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder={
              searchType === 'names'
                ? 'Search for a name (e.g., Abraham, Moses, God)'
                : 'Search for text in verses'
            }
            icon={<SearchIcon className="w-4 h-4" />}
            className="text-lg"
          />

          <Tabs defaultValue="names" value={searchType} onValueChange={(v) => setSearchType(v as 'names' | 'verses')}>
            <TabsList>
              <TabsTrigger value="names">
                <Users className="w-4 h-4 mr-2" />
                Names
              </TabsTrigger>
              <TabsTrigger value="verses">
                <FileText className="w-4 h-4 mr-2" />
                Verses
              </TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Options */}
          <div className="flex flex-wrap items-center gap-4 pt-2 border-t border-ink-lighter">
            <label className="flex items-center gap-2 text-sm text-parchment-200/70 cursor-pointer">
              <input
                type="checkbox"
                checked={includeHebrew}
                onChange={(e) => setIncludeHebrew(e.target.checked)}
                className="rounded border-ink-lighter bg-ink-lighter text-gold-600 focus:ring-gold-600/30"
              />
              Include Hebrew text
            </label>

            {searchType === 'names' && (
              <label className="flex items-center gap-2 text-sm text-parchment-200/70 cursor-pointer">
                <input
                  type="checkbox"
                  checked={exactMatch}
                  onChange={(e) => setExactMatch(e.target.checked)}
                  className="rounded border-ink-lighter bg-ink-lighter text-gold-600 focus:ring-gold-600/30"
                />
                Exact match only
              </label>
            )}

            {searchType === 'verses' && (
              <Select
                value={bookFilter}
                onChange={(e) => setBookFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Books' },
                  ...TORAH_BOOKS.map((b) => ({ value: b.name, label: b.name })),
                ]}
                className="w-36"
              />
            )}
          </div>
        </div>
      </Card>

      {/* Recent searches */}
      {!query && recentSearches.length > 0 && (
        <Card variant="bordered" className="p-4 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-parchment-200/60">Recent searches</span>
            <button
              onClick={clearRecentSearches}
              className="text-xs text-parchment-200/40 hover:text-gold-500 transition-colors"
            >
              Clear all
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((search) => (
              <button
                key={search}
                onClick={() => handleSearch(search)}
                className="px-3 py-1.5 text-sm bg-ink-lighter rounded-lg text-parchment-200 hover:bg-ink-soft hover:text-gold-400 transition-colors"
              >
                {search}
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Results */}
      {query && (
        <div>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-ink-soft rounded-lg p-4">
                  <Skeleton className="h-5 w-48 mb-2" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ))}
            </div>
          ) : hasResults ? (
            <div className="space-y-4">
              <p className="text-sm text-parchment-200/50">
                Found{' '}
                {searchType === 'names'
                  ? `${nameResults?.length} names`
                  : `${verseResults?.length} verses`}
              </p>

              {searchType === 'names'
                ? nameResults?.map((name, idx) => (
                    <Card
                      key={name.id}
                      hover
                      variant="bordered"
                      className="p-4 animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
                    >
                      <div className="flex items-center justify-between">
                        <NameBadge
                          name={name.name}
                          hebrew={name.hebrew}
                          type={name.type}
                        />
                        <div className="text-right">
                          <span className="text-gold-500">{formatNumber(name.occurrences)}</span>
                          <span className="text-parchment-200/40 text-sm ml-1">occ.</span>
                        </div>
                      </div>
                      {name.first_mention && (
                        <p className="text-xs text-parchment-200/50 mt-2">
                          First mention: {name.first_mention}
                        </p>
                      )}
                    </Card>
                  ))
                : verseResults?.map((verse, idx) => (
                    <div
                      key={verse.id}
                      className="animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
                    >
                      <VerseCard verse={verse} highlight={query} compact />
                    </div>
                  ))}
            </div>
          ) : debouncedQuery.length > 0 ? (
            <Card variant="bordered" className="p-8 text-center">
              <SearchIcon className="w-12 h-12 text-parchment-200/20 mx-auto mb-4" />
              <p className="text-parchment-200/60">
                No {searchType} found for "{debouncedQuery}"
              </p>
              <p className="text-sm text-parchment-200/40 mt-2">
                Try a different search term or adjust filters
              </p>
            </Card>
          ) : null}
        </div>
      )}

      {/* Empty state */}
      {!query && !recentSearches.length && (
        <Card variant="bordered" className="p-8 text-center">
          <SearchIcon className="w-12 h-12 text-gold-600/30 mx-auto mb-4" />
          <p className="text-parchment-200/60">
            Enter a search term to find names or verses
          </p>
        </Card>
      )}
    </div>
  );
}
