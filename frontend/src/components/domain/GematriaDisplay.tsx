import { cn, formatNumber, GEMATRIA_METHODS } from '../../lib/utils';
import type { GematriaCalculation } from '../../api/types';

interface GematriaDisplayProps {
  data: GematriaCalculation;
  compact?: boolean;
  className?: string;
}

export function GematriaDisplay({ data, compact = false, className }: GematriaDisplayProps) {
  const methods = [
    { key: 'standard', value: data.standard },
    { key: 'katan', value: data.katan },
    { key: 'ordinal', value: data.ordinal },
    { key: 'atbash', value: data.atbash },
  ] as const;

  if (compact) {
    return (
      <div className={cn('flex items-center gap-3 text-sm', className)}>
        {methods.map(({ key, value }) => (
          <span key={key} className="text-parchment-200/60">
            <span className="text-gold-600 capitalize">{key}:</span>{' '}
            <span className="text-parchment-100">{formatNumber(value)}</span>
          </span>
        ))}
      </div>
    );
  }

  return (
    <div className={cn('grid grid-cols-2 sm:grid-cols-4 gap-4', className)}>
      {methods.map(({ key, value }) => {
        const method = GEMATRIA_METHODS.find((m) => m.value === key);
        return (
          <div
            key={key}
            className="bg-ink-lighter rounded-lg p-4 text-center border border-ink-lighter"
          >
            <div className="text-3xl font-display text-gold-400 mb-1">
              {formatNumber(value)}
            </div>
            <div className="text-sm text-parchment-100 font-medium">
              {method?.label}
            </div>
            <div className="text-xs text-parchment-200/50 mt-0.5">
              {method?.description}
            </div>
          </div>
        );
      })}
    </div>
  );
}
