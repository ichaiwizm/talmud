import { cn } from '../../lib/utils';

interface HebrewTextProps {
  children: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function HebrewText({ children, size = 'md', className }: HebrewTextProps) {
  return (
    <span
      className={cn(
        'hebrew',
        size === 'sm' && 'text-sm',
        size === 'md' && 'text-base',
        size === 'lg' && 'text-xl',
        size === 'xl' && 'text-2xl hebrew-large',
        className
      )}
    >
      {children}
    </span>
  );
}
