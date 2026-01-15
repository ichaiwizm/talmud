import { Link, useParams } from 'react-router-dom';
import { ChevronRight, MapPin, Clock, Users2, BookOpen } from 'lucide-react';
import {
  useName,
  useNameTimeline,
  useNameCoOccurrences,
  useNameNearby,
} from '../../hooks/useApi';
import { HebrewText } from '../../components/domain/HebrewText';
import { VerseCard } from '../../components/domain/VerseCard';
import { NameBadge } from '../../components/domain/NameBadge';
import { Card } from '../../components/ui/Card';
import { Tabs, TabsList, TabsTrigger, TabsContent, Badge } from '../../components/ui';
import { TypeBadge } from '../../components/ui/Badge';
import { Loading, Skeleton, SkeletonVerse } from '../../components/ui/Loading';
import { formatNumber, TORAH_BOOKS } from '../../lib/utils';
import type { VerseResponse } from '../../api/types';

export function NameDetail() {
  const { name: nameParam } = useParams<{ name: string }>();
  const name = decodeURIComponent(nameParam || '');

  const { data: nameData, isLoading, error } = useName(name);
  const { data: timeline } = useNameTimeline(name);
  const { data: coOccurrences } = useNameCoOccurrences(name, { limit: 20 });
  const { data: nearby } = useNameNearby(name, { radius: 3, limit: 20 });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Skeleton className="w-48 h-4 mb-4" />
          <Skeleton className="w-64 h-10 mb-2" />
          <Skeleton className="w-32 h-6" />
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <SkeletonVerse key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !nameData) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Name not found</p>
        <Link to="/names" className="text-gold-500 hover:text-gold-400 mt-2 inline-block">
          Back to names
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-parchment-200/60 mb-6">
        <Link to="/names" className="hover:text-gold-400 transition-colors">
          Names
        </Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-parchment-100">{nameData.name}</span>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start gap-4 mb-4">
          <TypeBadge type={nameData.type} className="mt-1" />
          <div>
            {nameData.hebrew && (
              <HebrewText size="xl" className="text-gold-400 block mb-1">
                {nameData.hebrew}
              </HebrewText>
            )}
            <h1 className="display-heading text-4xl text-parchment-50">
              {nameData.name}
            </h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-parchment-200/60">
          <span>
            <span className="text-gold-500 font-medium">
              {formatNumber(nameData.occurrences)}
            </span>{' '}
            occurrences
          </span>
          {nameData.first_mention && (
            <span className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              First mention: {nameData.first_mention}
            </span>
          )}
        </div>

        {nameData.description && (
          <p className="mt-4 text-parchment-200/70 max-w-2xl">
            {nameData.description}
          </p>
        )}
      </div>

      {/* Tabs */}
      <Tabs defaultValue="occurrences">
        <TabsList className="mb-6">
          <TabsTrigger value="occurrences">
            <BookOpen className="w-4 h-4 mr-2" />
            Occurrences
          </TabsTrigger>
          <TabsTrigger value="timeline">
            <Clock className="w-4 h-4 mr-2" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="relations">
            <Users2 className="w-4 h-4 mr-2" />
            Relations
          </TabsTrigger>
        </TabsList>

        {/* Occurrences Tab */}
        <TabsContent value="occurrences">
          <div className="space-y-4">
            {nameData.verses.slice(0, 20).map((verse, idx) => (
              <div
                key={idx}
                className="animate-slide-up opacity-0"
                style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
              >
                <VerseCard
                  verse={verse as unknown as VerseResponse}
                  highlight={verse.surface_form}
                  compact
                />
              </div>
            ))}
            {nameData.verses.length > 20 && (
              <p className="text-center text-parchment-200/50 py-4">
                Showing 20 of {nameData.verses.length} occurrences
              </p>
            )}
          </div>
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value="timeline">
          {timeline ? (
            <div className="space-y-6">
              {/* Book distribution */}
              <Card variant="bordered" className="p-6">
                <h3 className="display-heading text-lg text-parchment-100 mb-4">
                  Distribution by Book
                </h3>
                <div className="space-y-3">
                  {TORAH_BOOKS.map((book) => {
                    const count = timeline.by_book[book.name] || 0;
                    const maxCount = Math.max(...Object.values(timeline.by_book));
                    const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    return (
                      <div key={book.name} className="flex items-center gap-4">
                        <span className="w-28 text-parchment-100">{book.name}</span>
                        <div className="flex-1 h-6 bg-ink-lighter rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-gold-700 to-gold-600 rounded-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="w-12 text-right text-gold-500 font-medium">
                          {count}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Timeline list */}
              <div>
                <h3 className="display-heading text-lg text-parchment-100 mb-4">
                  Chronological Appearances
                </h3>
                <div className="relative pl-6 border-l border-gold-700/30">
                  {timeline.timeline.slice(0, 30).map((entry, idx) => (
                    <div
                      key={idx}
                      className="relative pb-4 animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
                    >
                      <div className="absolute -left-[25px] w-3 h-3 rounded-full bg-gold-600 border-2 border-ink" />
                      <Link
                        to={`/books/${entry.book}/${entry.chapter}/${entry.verse}`}
                        className="text-parchment-100 hover:text-gold-400 transition-colors"
                      >
                        {entry.ref}
                      </Link>
                      <span className="text-parchment-200/50 text-sm ml-2">
                        as "{entry.surface_form}"
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <Loading className="py-12" />
          )}
        </TabsContent>

        {/* Relations Tab */}
        <TabsContent value="relations">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Co-occurrences */}
            <Card variant="bordered" className="p-6">
              <h3 className="display-heading text-lg text-parchment-100 mb-4">
                Appears Together With
              </h3>
              <p className="text-sm text-parchment-200/50 mb-4">
                Names that appear in the same verses
              </p>
              {coOccurrences ? (
                <div className="space-y-2">
                  {coOccurrences.co_occurrences.map((co, idx) => (
                    <div
                      key={co.name}
                      className="flex items-center justify-between p-2 rounded hover:bg-ink-lighter/50 transition-colors animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
                    >
                      <NameBadge
                        name={co.name}
                        hebrew={co.hebrew}
                        type={co.type}
                        size="sm"
                      />
                      <Badge variant="outline">{co.count}x</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <Loading className="py-8" />
              )}
            </Card>

            {/* Nearby names */}
            <Card variant="bordered" className="p-6">
              <h3 className="display-heading text-lg text-parchment-100 mb-4">
                Nearby Names
              </h3>
              <p className="text-sm text-parchment-200/50 mb-4">
                Names appearing within 3 verses
              </p>
              {nearby ? (
                <div className="space-y-2">
                  {nearby.map((n, idx) => (
                    <div
                      key={n.name}
                      className="flex items-center justify-between p-2 rounded hover:bg-ink-lighter/50 transition-colors animate-fade-in opacity-0"
                      style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
                    >
                      <NameBadge
                        name={n.name}
                        hebrew={n.hebrew}
                        type={n.type}
                        size="sm"
                      />
                      <div className="text-right">
                        <span className="text-gold-500 text-sm">{n.count}x</span>
                        <span className="text-parchment-200/40 text-xs ml-2">
                          avg {n.avg_distance.toFixed(1)}v
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Loading className="py-8" />
              )}
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
