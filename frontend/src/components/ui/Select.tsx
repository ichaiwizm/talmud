import { forwardRef, type SelectHTMLAttributes } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: Array<{ value: string; label: string }>;
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, options, placeholder, ...props }, ref) => {
    return (
      <div className="relative">
        <select
          ref={ref}
          className={cn(
            'w-full h-10 px-3 py-2 pr-10 rounded appearance-none',
            'bg-ink-lighter border border-ink-lighter',
            'text-parchment-100',
            'transition-colors duration-200',
            'hover:border-gold-700/30',
            'focus:outline-none focus:border-gold-600/50 focus:ring-1 focus:ring-gold-600/30',
            'cursor-pointer',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" className="text-parchment-200/40">
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-ink-soft">
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-parchment-200/50 pointer-events-none" />
      </div>
    );
  }
);

Select.displayName = 'Select';
