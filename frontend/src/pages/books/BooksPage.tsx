import { useBooks } from '../../hooks/useApi';
import { BookCard } from '../../components/domain/BookCard';
import { Skeleton } from '../../components/ui/Loading';

export function BooksPage() {
  const { data: books, isLoading, error } = useBooks();

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="display-heading text-3xl text-parchment-50 mb-2">
          Torah Books
        </h1>
        <p className="text-parchment-200/60">
          The Five Books of Moses - Chumash
        </p>
      </div>

      {/* Books grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-ink-soft rounded-lg p-6 h-48 animate-pulse">
              <Skeleton className="w-12 h-12 mb-4" />
              <Skeleton className="w-24 h-8 mb-2" />
              <Skeleton className="w-32 h-6 mb-4" />
              <Skeleton className="w-20 h-4" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-400">Failed to load books</p>
        </div>
      ) : books ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {books.map((book, idx) => (
            <div
              key={book.id}
              className="animate-slide-up opacity-0"
              style={{ animationDelay: `${idx * 100}ms`, animationFillMode: 'forwards' }}
            >
              <BookCard book={book} />
            </div>
          ))}
        </div>
      ) : null}

      {/* Hebrew footer */}
      <div className="mt-12 text-center">
        <p className="hebrew text-2xl text-gold-600/40">
          בראשית שמות ויקרא במדבר דברים
        </p>
        <p className="text-xs text-parchment-200/30 mt-2">
          Genesis, Exodus, Leviticus, Numbers, Deuteronomy
        </p>
      </div>
    </div>
  );
}
