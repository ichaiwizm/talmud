import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, icon, ...props }, ref) => {
    return (
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-parchment-200/50">
            {icon}
          </div>
        )}
        <input
          ref={ref}
          className={cn(
            'w-full h-10 px-3 py-2 rounded',
            'bg-ink-lighter border border-ink-lighter',
            'text-parchment-100 placeholder:text-parchment-200/40',
            'transition-colors duration-200',
            'hover:border-gold-700/30',
            'focus:outline-none focus:border-gold-600/50 focus:ring-1 focus:ring-gold-600/30',
            icon && 'pl-10',
            className
          )}
          {...props}
        />
      </div>
    );
  }
);

Input.displayName = 'Input';
