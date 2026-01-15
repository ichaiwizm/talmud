import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(
          'inline-flex items-center justify-center font-medium transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold-500 focus-visible:ring-offset-2 focus-visible:ring-offset-ink',
          'disabled:pointer-events-none disabled:opacity-50',
          // Variants
          variant === 'primary' && [
            'bg-gold-600 text-ink hover:bg-gold-500',
            'shadow-sm shadow-gold-900/20',
          ],
          variant === 'secondary' && [
            'bg-ink-lighter text-parchment-100 hover:bg-ink-soft',
            'border border-ink-lighter hover:border-gold-700/30',
          ],
          variant === 'ghost' && [
            'text-parchment-200 hover:text-gold-400 hover:bg-ink-soft/50',
          ],
          variant === 'outline' && [
            'border border-gold-700/40 text-gold-400 hover:bg-gold-700/10',
            'hover:border-gold-600/60',
          ],
          // Sizes
          size === 'sm' && 'h-8 px-3 text-sm rounded',
          size === 'md' && 'h-10 px-4 text-sm rounded',
          size === 'lg' && 'h-12 px-6 text-base rounded-lg',
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
