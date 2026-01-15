import { type HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';
import type { NameType } from '../../api/types';
import { NAME_TYPE_COLORS, NAME_TYPE_LABELS } from '../../lib/utils';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'outline';
}

export function Badge({ className, variant = 'default', children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded',
        variant === 'default' && 'bg-ink-lighter text-parchment-200',
        variant === 'outline' && 'border border-ink-lighter text-parchment-200',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

interface TypeBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  type: NameType;
  showLabel?: boolean;
}

export function TypeBadge({ type, showLabel = true, className, ...props }: TypeBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-1 text-xs font-medium rounded',
        'text-parchment-50',
        NAME_TYPE_COLORS[type],
        className
      )}
      {...props}
    >
      {showLabel ? NAME_TYPE_LABELS[type] : type}
    </span>
  );
}
