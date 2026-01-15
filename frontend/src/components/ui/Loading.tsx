import { cn } from '../../lib/utils';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Loading({ size = 'md', className }: LoadingProps) {
  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          'border-2 border-parchment-200/20 border-t-gold-500 rounded-full animate-spin',
          size === 'sm' && 'w-4 h-4',
          size === 'md' && 'w-8 h-8',
          size === 'lg' && 'w-12 h-12'
        )}
      />
    </div>
  );
}

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cn('animate-shimmer rounded', className)} />;
}

export function SkeletonCard() {
  return (
    <div className="bg-ink-soft rounded-lg p-5 space-y-3">
      <Skeleton className="h-5 w-2/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-4/5" />
    </div>
  );
}

export function SkeletonVerse() {
  return (
    <div className="bg-ink-soft rounded-lg p-5 space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-6 w-20" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-3/4" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>
    </div>
  );
}
