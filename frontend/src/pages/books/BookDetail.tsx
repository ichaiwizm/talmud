import { Link, useParams } from 'react-router-dom';
import { ChevronRight, BookOpen } from 'lucide-react';
import { useBook } from '../../hooks/useApi';
import { HebrewText } from '../../components/domain/HebrewText';
import { Skeleton } from '../../components/ui/Loading';
import { cn } from '../../lib/utils';

export function BookDetail() {
  const { book: bookName } = useParams<{ book: string }>();
  const { data: book, isLoading, error } = useBook(bookName || '');

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Skeleton className="w-48 h-8 mb-2" />
          <Skeleton className="w-32 h-6" />
        </div>
        <div className="grid grid-cols-5 sm:grid-cols-8 md:grid-cols-10 gap-3">
          {[...Array(50)].map((_, i) => (
            <Skeleton key={i} className="aspect-square rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Book not found</p>
        <Link to="/books" className="text-gold-500 hover:text-gold-400 mt-2 inline-block">
          Back to books
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-parchment-200/60 mb-6">
        <Link to="/books" className="hover:text-gold-400 transition-colors">
          Torah
        </Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-parchment-100">{book.name}</span>
      </nav>

      {/* Header */}
      <div className="mb-8 flex items-start gap-6">
        <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-gold-600 to-gold-700 flex items-center justify-center shadow-lg shadow-gold-900/30">
          <BookOpen className="w-8 h-8 text-ink" />
        </div>
        <div>
          <HebrewText size="xl" className="text-gold-400 block mb-1">
            {book.hebrew_name}
          </HebrewText>
          <h1 className="display-heading text-3xl text-parchment-50">
            {book.name}
          </h1>
          <p className="text-parchment-200/60 mt-1">
            {book.total_chapters} chapters
          </p>
        </div>
      </div>

      {/* Chapters grid */}
      <div className="grid grid-cols-5 sm:grid-cols-8 md:grid-cols-10 gap-3">
        {book.chapters.map((chapter, idx) => (
          <Link
            key={chapter.number}
            to={`/books/${book.name}/${chapter.number}`}
            className={cn(
              'aspect-square rounded-lg bg-ink-soft border border-ink-lighter',
              'flex flex-col items-center justify-center gap-1',
              'hover:border-gold-700/40 hover:bg-ink-lighter transition-all duration-200',
              'group animate-fade-in opacity-0'
            )}
            style={{ animationDelay: `${idx * 20}ms`, animationFillMode: 'forwards' }}
          >
            <span className="text-lg font-medium text-parchment-100 group-hover:text-gold-400 transition-colors">
              {chapter.number}
            </span>
            <span className="text-[10px] text-parchment-200/40">
              {chapter.total_verses}v
            </span>
          </Link>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-8 text-center">
        <p className="text-xs text-parchment-200/40">
          Select a chapter to view its verses
        </p>
      </div>
    </div>
  );
}
