import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Filter, ArrowUpDown } from 'lucide-react';
import { useNames } from '../../hooks/useApi';
import { useUIStore } from '../../store';
import { Card } from '../../components/ui/Card';
import { Select, Pagination } from '../../components/ui';
import { Skeleton } from '../../components/ui/Loading';
import { TypeBadge } from '../../components/ui/Badge';
import { formatNumber, NAME_TYPE_LABELS, TORAH_BOOKS } from '../../lib/utils';
import type { NameType } from '../../api/types';

const PAGE_SIZE = 50;

const NAME_TYPES: Array<{ value: string; label: string }> = [
  { value: '', label: 'All Types' },
  ...Object.entries(NAME_TYPE_LABELS).map(([value, label]) => ({ value, label })),
];

const SORT_OPTIONS = [
  { value: 'frequency', label: 'By Frequency' },
  { value: 'alpha', label: 'Alphabetical' },
];

export function NamesPage() {
  const { namesFilter, setNamesFilter } = useUIStore();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useNames({
    name_type: namesFilter.type || undefined,
    book: namesFilter.book || undefined,
    sort_by: namesFilter.sortBy,
    limit: PAGE_SIZE,
    offset: (page - 1) * PAGE_SIZE,
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-gold-500" />
          <h1 className="display-heading text-3xl text-parchment-50">
            Biblical Names
          </h1>
        </div>
        <p className="text-parchment-200/60">
          Explore names of people, places, and divine beings in the Torah
        </p>
      </div>

      {/* Filters */}
      <Card variant="bordered" className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-parchment-200/60">
            <Filter className="w-4 h-4" />
            <span className="text-sm">Filters:</span>
          </div>
          <Select
            value={namesFilter.type || ''}
            onChange={(e) => {
              setNamesFilter({ type: (e.target.value as NameType) || null });
              setPage(1);
            }}
            options={NAME_TYPES}
            className="w-40"
          />
          <Select
            value={namesFilter.book || ''}
            onChange={(e) => {
              setNamesFilter({ book: e.target.value || null });
              setPage(1);
            }}
            options={[
              { value: '', label: 'All Books' },
              ...TORAH_BOOKS.map((b) => ({ value: b.name, label: b.name })),
            ]}
            className="w-40"
          />
          <div className="flex items-center gap-2 ml-auto">
            <ArrowUpDown className="w-4 h-4 text-parchment-200/60" />
            <Select
              value={namesFilter.sortBy}
              onChange={(e) => {
                setNamesFilter({ sortBy: e.target.value as 'frequency' | 'alpha' });
                setPage(1);
              }}
              options={SORT_OPTIONS}
              className="w-36"
            />
          </div>
        </div>
      </Card>

      {/* Results info */}
      {data && (
        <p className="text-sm text-parchment-200/50 mb-4">
          Showing {(page - 1) * PAGE_SIZE + 1}-
          {Math.min(page * PAGE_SIZE, data.total)} of {formatNumber(data.total)} names
        </p>
      )}

      {/* Names list */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="bg-ink-soft rounded-lg p-4 flex items-center gap-4">
              <Skeleton className="w-3 h-3 rounded-full" />
              <Skeleton className="w-32 h-5" />
              <Skeleton className="w-16 h-5" />
              <Skeleton className="w-20 h-5 ml-auto" />
            </div>
          ))}
        </div>
      ) : data?.items ? (
        <div className="space-y-2">
          {data.items.map((name, idx) => (
            <Link
              key={name.id}
              to={`/names/${encodeURIComponent(name.name)}`}
              className="block animate-fade-in opacity-0"
              style={{ animationDelay: `${idx * 20}ms`, animationFillMode: 'forwards' }}
            >
              <Card
                hover
                variant="bordered"
                className="p-4 flex items-center gap-4"
              >
                <TypeBadge type={name.type} className="w-20 justify-center" />
                <div className="flex-1 min-w-0">
                  <span className="text-parchment-100 font-medium">{name.name}</span>
                  {name.hebrew && (
                    <span className="hebrew text-parchment-200/60 ml-3">
                      {name.hebrew}
                    </span>
                  )}
                </div>
                <div className="text-right">
                  <span className="text-gold-500 font-medium">
                    {formatNumber(name.occurrences)}
                  </span>
                  <span className="text-parchment-200/40 text-sm ml-1">
                    occurrences
                  </span>
                </div>
                {name.first_mention && (
                  <span className="text-xs text-parchment-200/40 hidden md:block">
                    First: {name.first_mention}
                  </span>
                )}
              </Card>
            </Link>
          ))}
        </div>
      ) : null}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8">
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  );
}
