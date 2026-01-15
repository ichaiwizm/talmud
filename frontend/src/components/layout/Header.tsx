import { Menu, Scroll } from 'lucide-react';
import { useHealth } from '../../hooks/useApi';
import { useUIStore } from '../../store';
import { cn } from '../../lib/utils';

export function Header() {
  const { toggleSidebar } = useUIStore();
  const { data: health, isError } = useHealth();

  return (
    <header className="h-16 bg-ink-soft/80 backdrop-blur-sm border-b border-ink-lighter sticky top-0 z-40">
      <div className="h-full px-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg text-parchment-200 hover:text-gold-400 hover:bg-ink-lighter transition-colors lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-gold-600 to-gold-700 flex items-center justify-center shadow-lg shadow-gold-900/30">
              <Scroll className="w-5 h-5 text-ink" />
            </div>
            <div className="hidden sm:block">
              <h1 className="display-heading text-xl text-parchment-50">
                Torah Analysis
              </h1>
              <p className="text-xs text-parchment-200/50 -mt-0.5">
                Explore the sacred text
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                'w-2 h-2 rounded-full',
                health?.status === 'ok' ? 'bg-green-500' : isError ? 'bg-red-500' : 'bg-yellow-500'
              )}
            />
            <span className="text-xs text-parchment-200/50 hidden sm:inline">
              {health?.status === 'ok' ? 'API Connected' : isError ? 'API Error' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
