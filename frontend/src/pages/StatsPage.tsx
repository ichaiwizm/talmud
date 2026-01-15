import { useState } from 'react';
import { BarChart3, TrendingUp, Link as LinkIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useGlobalStats, useTopNames, useNamePairs } from '../hooks/useApi';
import { NameBadge } from '../components/domain/NameBadge';
import { StatCard } from '../components/domain/StatCard';
import { Card } from '../components/ui/Card';
import { Select } from '../components/ui';
import { Loading, Skeleton } from '../components/ui/Loading';
import { formatNumber, NAME_TYPE_LABELS } from '../lib/utils';
import type { NameType } from '../api/types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';

const TYPE_COLORS: Record<NameType, string> = {
  person: '#1e3a5f',
  deity: '#d4a012',
  place: '#2d4a3e',
  people_group: '#4a3252',
  angel: '#5e3a6e',
  unknown: '#2d2a26',
};

export function StatsPage() {
  const [topNamesLimit, setTopNamesLimit] = useState(20);
  const [typeFilter, setTypeFilter] = useState<NameType | ''>('');

  const { data: stats, isLoading: statsLoading } = useGlobalStats();
  const { data: topNames, isLoading: topNamesLoading } = useTopNames({
    limit: topNamesLimit,
    name_type: typeFilter || undefined,
  });
  const { data: pairs, isLoading: pairsLoading } = useNamePairs({ limit: 15 });

  // Prepare chart data
  const typeDistributionData = stats?.type_distribution
    ? Object.entries(stats.type_distribution).map(([type, count]) => ({
        name: NAME_TYPE_LABELS[type as NameType],
        value: count,
        type: type as NameType,
      }))
    : [];

  const topNamesChartData = topNames?.slice(0, 10).map((name) => ({
    name: name.name,
    occurrences: name.occurrences,
    type: name.type,
  }));

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="w-8 h-8 text-gold-500" />
          <h1 className="display-heading text-3xl text-parchment-50">Statistics</h1>
        </div>
        <p className="text-parchment-200/60">
          Explore patterns and insights from the Torah analysis
        </p>
      </div>

      {/* Overview stats */}
      {statsLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-lg" />
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Verses"
            value={stats.verses}
            description={`${stats.chapters} chapters in ${stats.books} books`}
          />
          <StatCard
            title="Processed"
            value={`${stats.progress_percent.toFixed(1)}%`}
            description={`${stats.processed} verses analyzed`}
          />
          <StatCard
            title="Unique Names"
            value={stats.unique_names}
            description="Distinct names found"
          />
          <StatCard
            title="Occurrences"
            value={stats.total_occurrences}
            description="Total name mentions"
          />
        </div>
      ) : null}

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Type distribution pie chart */}
        <Card variant="bordered" className="p-6">
          <h2 className="display-heading text-xl text-parchment-100 mb-6">
            Names by Type
          </h2>
          {typeDistributionData.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={typeDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, percent }: { name?: string; percent?: number }) =>
                      `${name || ''} (${((percent ?? 0) * 100).toFixed(0)}%)`
                    }
                    labelLine={{ stroke: '#5d5a55' }}
                  >
                    {typeDistributionData.map((entry) => (
                      <Cell
                        key={entry.type}
                        fill={TYPE_COLORS[entry.type]}
                        stroke="none"
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1c1a18',
                      border: '1px solid #2d2a26',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#f5f0e8' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <Loading className="py-20" />
          )}
        </Card>

        {/* Top names bar chart */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="display-heading text-xl text-parchment-100">
              Top Names
            </h2>
            <Link
              to="/names"
              className="text-sm text-gold-500 hover:text-gold-400"
            >
              View all
            </Link>
          </div>
          {topNamesChartData && topNamesChartData.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={topNamesChartData}
                  layout="vertical"
                  margin={{ left: 80, right: 20 }}
                >
                  <XAxis type="number" stroke="#5d5a55" />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="#5d5a55"
                    tick={{ fill: '#f5f0e8', fontSize: 12 }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1c1a18',
                      border: '1px solid #2d2a26',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#f5f0e8' }}
                  />
                  <Bar dataKey="occurrences" radius={[0, 4, 4, 0]}>
                    {topNamesChartData.map((entry) => (
                      <Cell
                        key={entry.name}
                        fill={TYPE_COLORS[entry.type]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <Loading className="py-20" />
          )}
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Top names list */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-gold-500" />
              <h2 className="display-heading text-lg text-parchment-100">
                Most Frequent Names
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <Select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as NameType | '')}
                options={[
                  { value: '', label: 'All' },
                  ...Object.entries(NAME_TYPE_LABELS).map(([value, label]) => ({
                    value,
                    label,
                  })),
                ]}
                className="w-28"
              />
              <Select
                value={String(topNamesLimit)}
                onChange={(e) => setTopNamesLimit(Number(e.target.value))}
                options={[
                  { value: '10', label: 'Top 10' },
                  { value: '20', label: 'Top 20' },
                  { value: '50', label: 'Top 50' },
                ]}
                className="w-24"
              />
            </div>
          </div>

          {topNamesLoading ? (
            <div className="space-y-2">
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-12 rounded-lg" />
              ))}
            </div>
          ) : topNames ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {topNames.map((name, idx) => (
                <div
                  key={name.id}
                  className="flex items-center gap-3 p-2 rounded hover:bg-ink-lighter/50 transition-colors"
                >
                  <span className="w-6 text-center text-gold-600 text-sm font-medium">
                    {idx + 1}
                  </span>
                  <NameBadge
                    name={name.name}
                    hebrew={name.hebrew}
                    type={name.type}
                    size="sm"
                  />
                  <span className="ml-auto text-gold-500 font-medium">
                    {formatNumber(name.occurrences)}
                  </span>
                </div>
              ))}
            </div>
          ) : null}
        </Card>

        {/* Name pairs */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <LinkIcon className="w-5 h-5 text-gold-500" />
            <h2 className="display-heading text-lg text-parchment-100">
              Most Common Pairs
            </h2>
          </div>
          <p className="text-sm text-parchment-200/50 mb-4">
            Names that appear together in the same verses most frequently
          </p>

          {pairsLoading ? (
            <div className="space-y-2">
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-12 rounded-lg" />
              ))}
            </div>
          ) : pairs ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {pairs.map((pair, idx) => (
                <div
                  key={`${pair.name1}-${pair.name2}`}
                  className="flex items-center gap-3 p-3 bg-ink-lighter/50 rounded-lg"
                >
                  <span className="w-6 text-center text-gold-600 text-sm font-medium">
                    {idx + 1}
                  </span>
                  <Link
                    to={`/names/${encodeURIComponent(pair.name1)}`}
                    className="text-parchment-100 hover:text-gold-400 transition-colors"
                  >
                    {pair.name1}
                  </Link>
                  <span className="text-parchment-200/30">+</span>
                  <Link
                    to={`/names/${encodeURIComponent(pair.name2)}`}
                    className="text-parchment-100 hover:text-gold-400 transition-colors"
                  >
                    {pair.name2}
                  </Link>
                  <span className="ml-auto text-gold-500 font-medium">
                    {pair.count}x
                  </span>
                </div>
              ))}
            </div>
          ) : null}

          <div className="mt-4 pt-4 border-t border-ink-lighter">
            <Link
              to="/graph"
              className="text-sm text-gold-500 hover:text-gold-400 flex items-center gap-1"
            >
              View relationship graph
              <svg
                className="w-4 h-4"
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
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
