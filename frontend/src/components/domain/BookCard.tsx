import { Link } from 'react-router-dom';
import { BookOpen, ChevronRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { HebrewText } from './HebrewText';
import { cn } from '../../lib/utils';
import type { BookSummary } from '../../api/types';

interface BookCardProps {
  book: BookSummary;
  className?: string;
}

export function BookCard({ book, className }: BookCardProps) {
  return (
    <Link to={`/books/${book.name}`}>
      <Card
        hover
        variant="bordered"
        className={cn(
          'p-6 group relative overflow-hidden',
          className
        )}
      >
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-gold-700/5 to-transparent rounded-bl-full" />

        {/* Order badge */}
        <div className="absolute top-4 right-4 w-8 h-8 rounded-full bg-gold-700/20 flex items-center justify-center">
          <span className="text-gold-500 text-sm font-medium">{book.order}</span>
        </div>

        <div className="relative">
          {/* Icon */}
          <div className="w-12 h-12 rounded-lg bg-gold-700/10 flex items-center justify-center mb-4 group-hover:bg-gold-700/20 transition-colors">
            <BookOpen className="w-6 h-6 text-gold-500" />
          </div>

          {/* Hebrew name (large) */}
          <HebrewText size="xl" className="text-parchment-50 block mb-1">
            {book.hebrew_name}
          </HebrewText>

          {/* English name */}
          <h3 className="display-heading text-xl text-parchment-100 mb-3">
            {book.name}
          </h3>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-parchment-200/60">
            <span>{book.total_chapters} chapters</span>
          </div>

          {/* Arrow */}
          <div className="absolute bottom-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <ChevronRight className="w-5 h-5 text-gold-500" />
          </div>
        </div>
      </Card>
    </Link>
  );
}
