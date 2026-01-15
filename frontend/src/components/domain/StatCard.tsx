import { type LucideIcon } from 'lucide-react';
import { Card } from '../ui/Card';
import { cn, formatNumber } from '../../lib/utils';

interface StatCardProps {
  title: string;
  value: number | string;
  icon?: LucideIcon;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function StatCard({
  title,
  value,
  icon: Icon,
  description,
  className,
}: StatCardProps) {
  const displayValue = typeof value === 'number' ? formatNumber(value) : value;

  return (
    <Card variant="bordered" className={cn('p-5', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-parchment-200/60 mb-1">{title}</p>
          <p className="display-heading text-3xl text-parchment-50">{displayValue}</p>
          {description && (
            <p className="text-xs text-parchment-200/40 mt-2">{description}</p>
          )}
        </div>
        {Icon && (
          <div className="p-2.5 rounded-lg bg-gold-700/10 text-gold-500">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </Card>
  );
}
