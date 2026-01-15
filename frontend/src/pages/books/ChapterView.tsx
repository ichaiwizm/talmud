import { Link, useParams, useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, ArrowLeft } from 'lucide-react';
import { useChapter, useBook } from '../../hooks/useApi';
import { VerseCard } from '../../components/domain/VerseCard';
import { Button } from '../../components/ui/Button';
import { SkeletonVerse } from '../../components/ui/Loading';

export function ChapterView() {
  const { book: bookName, chapter: chapterStr } = useParams<{
    book: string;
    chapter: string;
  }>();
  const chapter = parseInt(chapterStr || '1', 10);
  const navigate = useNavigate();

  const { data: chapterData, isLoading, error } = useChapter(bookName || '', chapter);
  const { data: book } = useBook(bookName || '');

  const totalChapters = book?.total_chapters || 0;
  const hasPrev = chapter > 1;
  const hasNext = chapter < totalChapters;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 space-y-2">
          <div className="h-4 w-48 animate-shimmer rounded" />
          <div className="h-8 w-64 animate-shimmer rounded" />
        </div>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <SkeletonVerse key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !chapterData) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Chapter not found</p>
        <Link
          to={`/books/${bookName}`}
          className="text-gold-500 hover:text-gold-400 mt-2 inline-block"
        >
          Back to {bookName}
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-parchment-200/60 mb-6">
        <Link to="/books" className="hover:text-gold-400 transition-colors">
          Torah
        </Link>
        <ChevronRight className="w-4 h-4" />
        <Link to={`/books/${bookName}`} className="hover:text-gold-400 transition-colors">
          {bookName}
        </Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-parchment-100">Chapter {chapter}</span>
      </nav>

      {/* Header with navigation */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="display-heading text-2xl text-parchment-50">
            {bookName} - Chapter {chapter}
          </h1>
          <p className="text-parchment-200/60 mt-1">
            {chapterData.total_verses} verses
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            disabled={!hasPrev}
            onClick={() => navigate(`/books/${bookName}/${chapter - 1}`)}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Prev
          </Button>
          <Button
            variant="ghost"
            size="sm"
            disabled={!hasNext}
            onClick={() => navigate(`/books/${bookName}/${chapter + 1}`)}
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      </div>

      {/* Verses */}
      <div className="space-y-4">
        {chapterData.verses.map((verse, idx) => (
          <div
            key={verse.id}
            className="animate-slide-up opacity-0"
            style={{ animationDelay: `${idx * 30}ms`, animationFillMode: 'forwards' }}
          >
            <VerseCard verse={verse} />
          </div>
        ))}
      </div>

      {/* Bottom navigation */}
      <div className="mt-8 flex items-center justify-between pt-6 border-t border-ink-lighter">
        <Link
          to={`/books/${bookName}`}
          className="inline-flex items-center gap-2 text-gold-500 hover:text-gold-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          All chapters
        </Link>
        <div className="flex items-center gap-2">
          {hasPrev && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/books/${bookName}/${chapter - 1}`)}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Chapter {chapter - 1}
            </Button>
          )}
          {hasNext && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => navigate(`/books/${bookName}/${chapter + 1}`)}
            >
              Chapter {chapter + 1}
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
