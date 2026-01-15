import { useState } from 'react';
import { Hash, Search, Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  useGematriaCalculate,
  useGematriaWords,
  useGematriaVerses,
} from '../hooks/useApi';
import { useUIStore } from '../store';
import { GematriaDisplay } from '../components/domain/GematriaDisplay';
import { HebrewText } from '../components/domain/HebrewText';
import { Card } from '../components/ui/Card';
import { Input, Select, Button, Tabs, TabsList, TabsTrigger } from '../components/ui';
import { Skeleton } from '../components/ui/Loading';
import { GEMATRIA_METHODS, TORAH_BOOKS, formatNumber, parseVerseRef } from '../lib/utils';
import { useDebounce } from '../hooks/useDebounce';
import type { GematriaMethod } from '../api/types';

export function GematriaPage() {
  const { defaultGematriaMethod, setDefaultGematriaMethod } = useUIStore();

  // Calculator state
  const [calcInput, setCalcInput] = useState('');
  const debouncedCalcInput = useDebounce(calcInput, 300);
  const { data: calcResult, isLoading: calcLoading } = useGematriaCalculate(debouncedCalcInput);

  // Search state
  const [searchValue, setSearchValue] = useState('');
  const [searchMethod, setSearchMethod] = useState<GematriaMethod>(defaultGematriaMethod);
  const [searchType, setSearchType] = useState<'words' | 'verses'>('words');
  const [bookFilter, setBookFilter] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const searchValueNum = parseInt(searchValue, 10);

  const { data: wordResults, isLoading: wordsLoading } = useGematriaWords(
    isSearching && searchType === 'words' ? searchValueNum : 0,
    { method: searchMethod, book: bookFilter || undefined, limit: 50 }
  );

  const { data: verseResults, isLoading: versesLoading } = useGematriaVerses(
    isSearching && searchType === 'verses' ? searchValueNum : 0,
    { method: searchMethod, book: bookFilter || undefined, limit: 50 }
  );

  const handleSearch = () => {
    if (searchValueNum > 0) {
      setIsSearching(true);
    }
  };

  const useCalculatedValue = () => {
    if (calcResult) {
      setSearchValue(String(calcResult[searchMethod]));
      setIsSearching(false);
    }
  };

  const isSearchLoading = searchType === 'words' ? wordsLoading : versesLoading;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Hash className="w-8 h-8 text-gold-500" />
          <h1 className="display-heading text-3xl text-parchment-50">Gematria</h1>
        </div>
        <p className="text-parchment-200/60">
          Calculate Hebrew numerological values and find textual connections
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Calculator */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center gap-2 mb-6">
            <Sparkles className="w-5 h-5 text-gold-500" />
            <h2 className="display-heading text-xl text-parchment-100">Calculator</h2>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm text-parchment-200/60 mb-2">
                Enter Hebrew text
              </label>
              <Input
                value={calcInput}
                onChange={(e) => setCalcInput(e.target.value)}
                placeholder="אברהם"
                className="hebrew text-xl text-right"
                dir="rtl"
              />
            </div>

            {calcLoading ? (
              <div className="grid grid-cols-2 gap-4">
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-24 rounded-lg" />
                ))}
              </div>
            ) : calcResult ? (
              <>
                <div className="text-center p-4 bg-ink-lighter rounded-lg border border-gold-700/30">
                  <HebrewText size="xl" className="text-gold-400">
                    {calcResult.text}
                  </HebrewText>
                </div>
                <GematriaDisplay data={calcResult} />
                <Button
                  variant="outline"
                  onClick={useCalculatedValue}
                  className="w-full"
                >
                  Use value for search
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </>
            ) : (
              <div className="text-center py-8 text-parchment-200/40">
                Enter Hebrew text to calculate gematria
              </div>
            )}
          </div>
        </Card>

        {/* Search */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center gap-2 mb-6">
            <Search className="w-5 h-5 text-gold-500" />
            <h2 className="display-heading text-xl text-parchment-100">Search by Value</h2>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-parchment-200/60 mb-2">
                  Gematria value
                </label>
                <Input
                  type="number"
                  value={searchValue}
                  onChange={(e) => {
                    setSearchValue(e.target.value);
                    setIsSearching(false);
                  }}
                  placeholder="Enter a number"
                  min={1}
                />
              </div>
              <div>
                <label className="block text-sm text-parchment-200/60 mb-2">Method</label>
                <Select
                  value={searchMethod}
                  onChange={(e) => {
                    setSearchMethod(e.target.value as GematriaMethod);
                    setDefaultGematriaMethod(e.target.value as GematriaMethod);
                    setIsSearching(false);
                  }}
                  options={GEMATRIA_METHODS.map((m) => ({
                    value: m.value,
                    label: m.label,
                  }))}
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Tabs
                defaultValue="words"
                value={searchType}
                onValueChange={(v) => {
                  setSearchType(v as 'words' | 'verses');
                  setIsSearching(false);
                }}
              >
                <TabsList>
                  <TabsTrigger value="words">Words</TabsTrigger>
                  <TabsTrigger value="verses">Verses</TabsTrigger>
                </TabsList>
              </Tabs>
              <Select
                value={bookFilter}
                onChange={(e) => {
                  setBookFilter(e.target.value);
                  setIsSearching(false);
                }}
                options={[
                  { value: '', label: 'All Books' },
                  ...TORAH_BOOKS.map((b) => ({ value: b.name, label: b.name })),
                ]}
                className="flex-1"
              />
            </div>

            <Button
              variant="primary"
              onClick={handleSearch}
              disabled={!searchValueNum}
              className="w-full"
            >
              <Search className="w-4 h-4 mr-2" />
              Find matches
            </Button>
          </div>
        </Card>
      </div>

      {/* Search Results */}
      {isSearching && (
        <Card variant="bordered" className="mt-6 p-6">
          <h3 className="display-heading text-lg text-parchment-100 mb-4">
            {searchType === 'words' ? 'Words' : 'Verses'} with gematria value{' '}
            <span className="text-gold-400">{searchValue}</span>
            <span className="text-parchment-200/50 text-sm ml-2">({searchMethod})</span>
          </h3>

          {isSearchLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-ink-lighter rounded-lg p-4">
                  <Skeleton className="h-5 w-32 mb-2" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ))}
            </div>
          ) : searchType === 'words' && wordResults ? (
            <div className="space-y-2">
              {wordResults.length === 0 ? (
                <p className="text-parchment-200/50 text-center py-8">
                  No words found with this value
                </p>
              ) : (
                wordResults.map((word, idx) => {
                  const parsed = parseVerseRef(word.verse_ref);
                  return (
                    <div
                      key={`${word.verse_ref}-${word.position}`}
                      className="p-4 bg-ink-lighter rounded-lg animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 20}ms`, animationFillMode: 'forwards' }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <HebrewText size="lg" className="text-gold-400">
                          {word.word}
                        </HebrewText>
                        <span className="text-gold-500 font-medium">{word.gematria}</span>
                      </div>
                      <Link
                        to={
                          parsed
                            ? `/books/${parsed.book}/${parsed.chapter}/${parsed.verse}`
                            : '#'
                        }
                        className="text-sm text-parchment-200/70 hover:text-gold-400 transition-colors"
                      >
                        {word.verse_ref}
                      </Link>
                    </div>
                  );
                })
              )}
              {wordResults.length > 0 && (
                <p className="text-sm text-parchment-200/50 text-center pt-4">
                  Found {wordResults.length} words
                </p>
              )}
            </div>
          ) : searchType === 'verses' && verseResults ? (
            <div className="space-y-3">
              {verseResults.length === 0 ? (
                <p className="text-parchment-200/50 text-center py-8">
                  No verses found with this total value
                </p>
              ) : (
                verseResults.map((verse, idx) => {
                  const parsed = parseVerseRef(verse.ref);
                  return (
                    <Link
                      key={verse.ref}
                      to={
                        parsed
                          ? `/books/${parsed.book}/${parsed.chapter}/${parsed.verse}`
                          : '#'
                      }
                      className="block p-4 bg-ink-lighter rounded-lg hover:bg-ink-soft transition-colors animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 20}ms`, animationFillMode: 'forwards' }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gold-500 text-sm">{verse.ref}</span>
                        <span className="text-gold-400 font-medium">
                          {formatNumber(verse.gematria)}
                        </span>
                      </div>
                      <HebrewText className="text-parchment-100 block mb-1">
                        {verse.text_hebrew.slice(0, 100) + (verse.text_hebrew.length > 100 ? '...' : '')}
                      </HebrewText>
                      <p className="text-sm text-parchment-200/60 line-clamp-2">
                        {verse.text_english}
                      </p>
                    </Link>
                  );
                })
              )}
            </div>
          ) : null}
        </Card>
      )}
    </div>
  );
}
