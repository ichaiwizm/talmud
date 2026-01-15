import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { NameType } from '../api/types';

interface NamesFilter {
  type: NameType | null;
  book: string | null;
  sortBy: 'frequency' | 'alpha';
}

interface UIStore {
  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Names filter
  namesFilter: NamesFilter;
  setNamesFilter: (filter: Partial<NamesFilter>) => void;
  resetNamesFilter: () => void;

  // Recent items
  recentSearches: string[];
  addRecentSearch: (query: string) => void;
  clearRecentSearches: () => void;

  // Gematria preferences
  defaultGematriaMethod: 'standard' | 'katan' | 'ordinal' | 'atbash';
  setDefaultGematriaMethod: (method: 'standard' | 'katan' | 'ordinal' | 'atbash') => void;
}

const defaultNamesFilter: NamesFilter = {
  type: null,
  book: null,
  sortBy: 'frequency',
};

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      // Sidebar
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      // Names filter
      namesFilter: defaultNamesFilter,
      setNamesFilter: (filter) =>
        set((state) => ({
          namesFilter: { ...state.namesFilter, ...filter },
        })),
      resetNamesFilter: () => set({ namesFilter: defaultNamesFilter }),

      // Recent searches
      recentSearches: [],
      addRecentSearch: (query) =>
        set((state) => ({
          recentSearches: [
            query,
            ...state.recentSearches.filter((s) => s !== query).slice(0, 9),
          ],
        })),
      clearRecentSearches: () => set({ recentSearches: [] }),

      // Gematria preferences
      defaultGematriaMethod: 'standard',
      setDefaultGematriaMethod: (method) => set({ defaultGematriaMethod: method }),
    }),
    {
      name: 'torah-ui-store',
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        namesFilter: state.namesFilter,
        recentSearches: state.recentSearches,
        defaultGematriaMethod: state.defaultGematriaMethod,
      }),
    }
  )
);
