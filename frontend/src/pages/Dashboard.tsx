import { Link } from 'react-router-dom';
import {
  BookOpen,
  Users,
  Hash,
  FileText,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { useGlobalStats, useTopNames } from '../hooks/useApi';
import { StatCard } from '../components/domain/StatCard';
import { NameBadge } from '../components/domain/NameBadge';
import { Card } from '../components/ui';
import { Loading } from '../components/ui/Loading';
import { formatNumber, NAME_TYPE_LABELS } from '../lib/utils';
import type { NameType } from '../api/types';

export function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useGlobalStats();
  const { data: topNames, isLoading: namesLoading } = useTopNames({ limit: 8 });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-ink-soft via-ink-soft to-ink-lighter border border-ink-lighter p-8 lg:p-12">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-radial from-gold-600/10 to-transparent rounded-full blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-2 text-gold-500 mb-4">
            <Sparkles className="w-5 h-5" />
            <span className="text-sm font-medium">Torah Analysis Platform</span>
          </div>
          <h1 className="display-heading text-4xl lg:text-5xl text-parchment-50 mb-4">
            Explore the Sacred Text
          </h1>
          <p className="text-parchment-200/70 max-w-2xl text-lg mb-8">
            Discover names, calculate gematria values, and uncover relationships
            within the Five Books of Moses through advanced textual analysis.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              to="/books"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gold-600 text-ink rounded-lg font-medium hover:bg-gold-500 transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              Browse Torah
            </Link>
            <Link
              to="/gematria"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-gold-700/40 text-gold-400 rounded-lg font-medium hover:bg-gold-700/10 transition-colors"
            >
              <Hash className="w-4 h-4" />
              Gematria Calculator
            </Link>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      {statsLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} variant="bordered" className="p-5 h-28 animate-pulse" />
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Torah Books"
            value={stats.books}
            icon={BookOpen}
            description="Five Books of Moses"
          />
          <StatCard
            title="Total Verses"
            value={stats.verses}
            icon={FileText}
            description={`${stats.chapters} chapters`}
          />
          <StatCard
            title="Unique Names"
            value={stats.unique_names}
            icon={Users}
            description={`${formatNumber(stats.total_occurrences)} occurrences`}
          />
          <StatCard
            title="Processing"
            value={`${stats.progress_percent.toFixed(0)}%`}
            icon={Hash}
            description={`${stats.processed} / ${stats.verses} verses`}
          />
        </div>
      ) : null}

      {/* Two column layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Top names */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="display-heading text-xl text-parchment-50">
              Most Frequent Names
            </h2>
            <Link
              to="/names"
              className="text-sm text-gold-500 hover:text-gold-400 flex items-center gap-1"
            >
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          {namesLoading ? (
            <Loading className="py-8" />
          ) : topNames ? (
            <div className="space-y-3">
              {topNames.map((name, idx) => (
                <div
                  key={name.id}
                  className="flex items-center gap-4 p-3 rounded-lg hover:bg-ink-lighter/50 transition-colors animate-fade-in"
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  <span className="w-6 text-center text-gold-600 font-medium">
                    {idx + 1}
                  </span>
                  <NameBadge
                    name={name.name}
                    hebrew={name.hebrew}
                    type={name.type}
                    linked
                  />
                  <span className="ml-auto text-parchment-200/50 text-sm">
                    {formatNumber(name.occurrences)} occurrences
                  </span>
                </div>
              ))}
            </div>
          ) : null}
        </Card>

        {/* Type distribution */}
        <Card variant="bordered" className="p-6">
          <h2 className="display-heading text-xl text-parchment-50 mb-6">
            Names by Type
          </h2>
          {stats?.type_distribution ? (
            <div className="space-y-4">
              {Object.entries(stats.type_distribution)
                .sort(([, a], [, b]) => b - a)
                .map(([type, count], idx) => {
                  const total = Object.values(stats.type_distribution).reduce(
                    (a, b) => a + b,
                    0
                  );
                  const percentage = (count / total) * 100;
                  return (
                    <div
                      key={type}
                      className="animate-fade-in"
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-parchment-100 font-medium">
                          {NAME_TYPE_LABELS[type as NameType]}
                        </span>
                        <span className="text-parchment-200/60 text-sm">
                          {formatNumber(count)}
                        </span>
                      </div>
                      <div className="h-2 bg-ink-lighter rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-1000 ease-out ${
                            type === 'person'
                              ? 'bg-torah-blue'
                              : type === 'deity'
                              ? 'bg-gold-600'
                              : type === 'place'
                              ? 'bg-torah-green'
                              : type === 'people_group'
                              ? 'bg-torah-purple'
                              : type === 'angel'
                              ? 'bg-[#5e3a6e]'
                              : 'bg-ink-lighter'
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          ) : (
            <Loading className="py-8" />
          )}
        </Card>
      </div>

      {/* Quick links */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Link
          to="/search"
          className="p-5 rounded-lg bg-ink-soft border border-ink-lighter hover:border-gold-700/30 transition-colors group"
        >
          <Users className="w-8 h-8 text-gold-600 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="display-heading text-lg text-parchment-100 mb-1">
            Search Names
          </h3>
          <p className="text-sm text-parchment-200/60">
            Find biblical names and their occurrences
          </p>
        </Link>
        <Link
          to="/graph"
          className="p-5 rounded-lg bg-ink-soft border border-ink-lighter hover:border-gold-700/30 transition-colors group"
        >
          <svg
            className="w-8 h-8 text-gold-600 mb-3 group-hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="5" cy="12" r="2" />
            <circle cx="19" cy="6" r="2" />
            <circle cx="19" cy="18" r="2" />
            <line x1="7" y1="12" x2="17" y2="6" />
            <line x1="7" y1="12" x2="17" y2="18" />
          </svg>
          <h3 className="display-heading text-lg text-parchment-100 mb-1">
            Relationship Graph
          </h3>
          <p className="text-sm text-parchment-200/60">
            Visualize name co-occurrences
          </p>
        </Link>
        <Link
          to="/stats"
          className="p-5 rounded-lg bg-ink-soft border border-ink-lighter hover:border-gold-700/30 transition-colors group"
        >
          <Hash className="w-8 h-8 text-gold-600 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="display-heading text-lg text-parchment-100 mb-1">
            Statistics
          </h3>
          <p className="text-sm text-parchment-200/60">
            Explore patterns and insights
          </p>
        </Link>
      </div>
    </div>
  );
}
