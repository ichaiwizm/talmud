import { X } from 'lucide-react';
import { Navigation } from './Navigation';
import { useUIStore } from '../../store';
import { cn } from '../../lib/utils';

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen } = useUIStore();

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 h-full w-64 bg-ink-soft border-r border-ink-lighter z-50',
          'transform transition-transform duration-300 ease-out',
          'lg:translate-x-0 lg:static lg:z-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Mobile close button */}
        <div className="flex items-center justify-between p-4 border-b border-ink-lighter lg:hidden">
          <span className="display-heading text-lg text-gold-400">Menu</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1 rounded text-parchment-200 hover:text-gold-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <div className="p-4 pt-6 lg:pt-4">
          <Navigation />
        </div>

        {/* Footer decoration */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-ink-lighter">
          <div className="text-center">
            <p className="hebrew text-gold-600/60 text-sm">תורה</p>
            <p className="text-[10px] text-parchment-200/30 mt-1">
              Five Books of Moses
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
