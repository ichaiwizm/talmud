import { Link } from 'react-router-dom';
import { cn, NAME_TYPE_COLORS, NAME_TYPE_LABELS } from '../../lib/utils';
import type { NameType } from '../../api/types';

interface NameBadgeProps {
  name: string;
  hebrew?: string | null;
  type: NameType;
  count?: number;
  linked?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function NameBadge({
  name,
  hebrew,
  type,
  count,
  linked = true,
  size = 'md',
  className,
}: NameBadgeProps) {
  const content = (
    <span
      className={cn(
        'inline-flex items-center gap-2 rounded-lg',
        'transition-all duration-200',
        size === 'sm' && 'px-2.5 py-1 text-sm',
        size === 'md' && 'px-3 py-1.5',
        'bg-ink-lighter border border-ink-lighter',
        linked && 'hover:border-gold-700/40 hover:bg-ink-soft cursor-pointer',
        className
      )}
    >
      <span
        className={cn(
          'w-2 h-2 rounded-full',
          NAME_TYPE_COLORS[type]
        )}
        title={NAME_TYPE_LABELS[type]}
      />
      <span className="text-parchment-100 font-medium">{name}</span>
      {hebrew && (
        <span className="hebrew text-parchment-200/60 text-sm">{hebrew}</span>
      )}
      {count !== undefined && (
        <span className="text-gold-500/70 text-sm">({count})</span>
      )}
    </span>
  );

  if (linked) {
    return <Link to={`/names/${encodeURIComponent(name)}`}>{content}</Link>;
  }

  return content;
}
