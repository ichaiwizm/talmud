import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import { Card } from '../ui/Card';
import { HebrewText } from './HebrewText';
import { cn, formatNumber, parseVerseRef } from '../../lib/utils';
import type { VerseResponse } from '../../api/types';

interface VerseCardProps {
  verse: VerseResponse;
  showLink?: boolean;
  highlight?: string;
  compact?: boolean;
  className?: string;
}

export function VerseCard({
  verse,
  showLink = true,
  highlight,
  compact = false,
  className,
}: VerseCardProps) {
  const parsed = parseVerseRef(verse.ref);
  const linkTo = parsed
    ? `/books/${parsed.book}/${parsed.chapter}/${parsed.verse}`
    : '#';

  const highlightText = (text: string, term: string): React.ReactNode => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-gold-600/30 text-parchment-50 rounded px-0.5">
          {part}
        </mark>
      ) : (
        <span key={i}>{part}</span>
      )
    );
  };

  return (
    <Card
      variant="bordered"
      hover={showLink}
      className={cn('group', className)}
    >
      <div className={cn('p-4', compact ? 'space-y-2' : 'space-y-4')}>
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-gold-500 text-sm font-medium">
              {verse.chapter}:{verse.verse}
            </span>
            <HebrewText size="sm" className="text-parchment-200/60 ml-2">
              {verse.he_ref}
            </HebrewText>
          </div>
          {showLink && (
            <Link
              to={linkTo}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-ink-lighter"
            >
              <ExternalLink className="w-4 h-4 text-gold-500" />
            </Link>
          )}
        </div>

        {/* Hebrew text */}
        <div className="border-l-2 border-gold-700/30 pl-4">
          {highlight ? (
            <span className={cn('hebrew block text-parchment-50', compact ? 'text-base' : 'text-xl hebrew-large')}>
              {highlightText(verse.text_hebrew, highlight)}
            </span>
          ) : (
            <HebrewText size={compact ? 'md' : 'lg'} className="text-parchment-50 block">
              {verse.text_hebrew}
            </HebrewText>
          )}
        </div>

        {/* English translation */}
        <p className={cn('text-parchment-200/70', compact ? 'text-sm' : 'text-base')}>
          {highlight ? highlightText(verse.text_english, highlight) : verse.text_english}
        </p>

        {/* Metadata */}
        {!compact && (verse.gematria_standard_total || verse.word_count) && (
          <div className="flex items-center gap-4 pt-2 border-t border-ink-lighter text-xs text-parchment-200/50">
            {verse.word_count && (
              <span>
                <span className="text-gold-600">Words:</span> {verse.word_count}
              </span>
            )}
            {verse.gematria_standard_total && (
              <span>
                <span className="text-gold-600">Gematria:</span>{' '}
                {formatNumber(verse.gematria_standard_total)}
              </span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
