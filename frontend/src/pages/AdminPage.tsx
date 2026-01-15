import { useState } from 'react';
import {
  Settings,
  Download,
  Users,
  Hash,
  CheckCircle2,
  AlertCircle,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import {
  useImportStatus,
  useExtractionStatus,
  useGematriaPopulationStatus,
  useHealth,
  useImportTorah,
  useStartExtraction,
  usePopulateGematria,
} from '../hooks/useApi';
import { Card } from '../components/ui/Card';
import { Button, Select, Input } from '../components/ui';
import { Loading } from '../components/ui/Loading';
import { formatNumber, TORAH_BOOKS } from '../lib/utils';

export function AdminPage() {
  const [extractionLimit, setExtractionLimit] = useState('');
  const [extractionBatchSize, setExtractionBatchSize] = useState('50');
  const [gematriaBook, setGematriaBook] = useState('');

  const { data: importStatus, isLoading: importLoading, refetch: refetchImport } = useImportStatus();
  const { data: extractionStatus, isLoading: extractionLoading, refetch: refetchExtraction } = useExtractionStatus();
  const { data: gematriaStatus, isLoading: gematriaLoading, refetch: refetchGematria } = useGematriaPopulationStatus();
  const { data: health, isError: healthError } = useHealth();

  const importMutation = useImportTorah();
  const extractionMutation = useStartExtraction();
  const gematriaMutation = usePopulateGematria();

  const handleImport = () => {
    importMutation.mutate();
  };

  const handleExtraction = () => {
    extractionMutation.mutate({
      limit: extractionLimit ? Number(extractionLimit) : undefined,
      batch_size: Number(extractionBatchSize),
      parallel: false,
    });
  };

  const handleGematriaPopulate = () => {
    gematriaMutation.mutate({
      book: gematriaBook || undefined,
    });
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Settings className="w-8 h-8 text-gold-500" />
          <h1 className="display-heading text-3xl text-parchment-50">Admin</h1>
        </div>
        <p className="text-parchment-200/60">
          Manage data import, name extraction, and gematria population
        </p>
      </div>

      {/* Health status */}
      <Card variant="bordered" className="p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-3 h-3 rounded-full ${
                health?.status === 'ok'
                  ? 'bg-green-500'
                  : healthError
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`}
            />
            <span className="text-parchment-100">
              API Status:{' '}
              {health?.status === 'ok'
                ? 'Connected'
                : healthError
                ? 'Error'
                : 'Checking...'}
            </span>
          </div>
          <span className="text-xs text-parchment-200/40">
            Auto-refresh every 30s
          </span>
        </div>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Torah Import */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Download className="w-5 h-5 text-gold-500" />
            <h2 className="display-heading text-lg text-parchment-100">
              Torah Import
            </h2>
          </div>

          {importLoading ? (
            <Loading className="py-8" />
          ) : importStatus ? (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-parchment-200/60">Books</span>
                  <span className="text-parchment-100">
                    {importStatus.books} / {importStatus.expected_books}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-parchment-200/60">Chapters</span>
                  <span className="text-parchment-100">{importStatus.chapters}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-parchment-200/60">Verses</span>
                  <span className="text-parchment-100">
                    {formatNumber(importStatus.verses)}
                  </span>
                </div>
              </div>

              {importStatus.books === importStatus.expected_books ? (
                <div className="flex items-center gap-2 text-green-500 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  All books imported
                </div>
              ) : (
                <Button
                  variant="primary"
                  onClick={handleImport}
                  disabled={importMutation.isPending}
                  className="w-full"
                >
                  {importMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Importing...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Import Torah
                    </>
                  )}
                </Button>
              )}

              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetchImport()}
                className="w-full"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          ) : null}
        </Card>

        {/* Name Extraction */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-gold-500" />
            <h2 className="display-heading text-lg text-parchment-100">
              Name Extraction
            </h2>
          </div>

          {extractionLoading ? (
            <Loading className="py-8" />
          ) : extractionStatus ? (
            <div className="space-y-4">
              {/* Progress bar */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-parchment-200/60">Progress</span>
                  <span className="text-gold-500">
                    {extractionStatus.progress_percent.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 bg-ink-lighter rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-gold-700 to-gold-500 rounded-full transition-all duration-500"
                    style={{ width: `${extractionStatus.progress_percent}%` }}
                  />
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-parchment-200/60">Processed</span>
                  <span className="text-parchment-100">
                    {formatNumber(extractionStatus.processed)} /{' '}
                    {formatNumber(extractionStatus.total_verses)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-parchment-200/60">Pending</span>
                  <span className="text-parchment-100">
                    {formatNumber(extractionStatus.pending)}
                  </span>
                </div>
                {extractionStatus.with_errors > 0 && (
                  <div className="flex justify-between text-red-400">
                    <span>Errors</span>
                    <span>{extractionStatus.with_errors}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-parchment-200/60">Names found</span>
                  <span className="text-gold-500">
                    {formatNumber(extractionStatus.unique_names)}
                  </span>
                </div>
              </div>

              {extractionStatus.pending > 0 && (
                <div className="space-y-2 pt-2 border-t border-ink-lighter">
                  <Input
                    type="number"
                    value={extractionLimit}
                    onChange={(e) => setExtractionLimit(e.target.value)}
                    placeholder="Limit (optional)"
                    className="text-sm"
                  />
                  <Select
                    value={extractionBatchSize}
                    onChange={(e) => setExtractionBatchSize(e.target.value)}
                    options={[
                      { value: '10', label: 'Batch: 10' },
                      { value: '25', label: 'Batch: 25' },
                      { value: '50', label: 'Batch: 50' },
                    ]}
                  />
                  <Button
                    variant="primary"
                    onClick={handleExtraction}
                    disabled={extractionMutation.isPending}
                    className="w-full"
                  >
                    {extractionMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Extracting...
                      </>
                    ) : (
                      <>
                        <Users className="w-4 h-4 mr-2" />
                        Start Extraction
                      </>
                    )}
                  </Button>
                </div>
              )}

              {extractionStatus.progress_percent === 100 && (
                <div className="flex items-center gap-2 text-green-500 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  Extraction complete
                </div>
              )}

              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetchExtraction()}
                className="w-full"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          ) : null}
        </Card>

        {/* Gematria Population */}
        <Card variant="bordered" className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Hash className="w-5 h-5 text-gold-500" />
            <h2 className="display-heading text-lg text-parchment-100">
              Gematria Data
            </h2>
          </div>

          {gematriaLoading ? (
            <Loading className="py-8" />
          ) : gematriaStatus ? (
            <div className="space-y-4">
              {/* Progress bar */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-parchment-200/60">Progress</span>
                  <span className="text-gold-500">
                    {gematriaStatus.progress_percent.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 bg-ink-lighter rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-gold-700 to-gold-500 rounded-full transition-all duration-500"
                    style={{ width: `${gematriaStatus.progress_percent}%` }}
                  />
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-parchment-200/60">Populated</span>
                  <span className="text-parchment-100">
                    {formatNumber(gematriaStatus.verses_populated)} /{' '}
                    {formatNumber(gematriaStatus.total_verses)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-parchment-200/60">Pending</span>
                  <span className="text-parchment-100">
                    {formatNumber(gematriaStatus.pending)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-parchment-200/60">Total words</span>
                  <span className="text-gold-500">
                    {formatNumber(gematriaStatus.total_words)}
                  </span>
                </div>
              </div>

              {gematriaStatus.pending > 0 && (
                <div className="space-y-2 pt-2 border-t border-ink-lighter">
                  <Select
                    value={gematriaBook}
                    onChange={(e) => setGematriaBook(e.target.value)}
                    options={[
                      { value: '', label: 'All Books' },
                      ...TORAH_BOOKS.map((b) => ({ value: b.name, label: b.name })),
                    ]}
                  />
                  <Button
                    variant="primary"
                    onClick={handleGematriaPopulate}
                    disabled={gematriaMutation.isPending}
                    className="w-full"
                  >
                    {gematriaMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Populating...
                      </>
                    ) : (
                      <>
                        <Hash className="w-4 h-4 mr-2" />
                        Populate
                      </>
                    )}
                  </Button>
                </div>
              )}

              {gematriaStatus.progress_percent === 100 && (
                <div className="flex items-center gap-2 text-green-500 text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  Population complete
                </div>
              )}

              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetchGematria()}
                className="w-full"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          ) : null}
        </Card>
      </div>

      {/* Info */}
      <Card variant="bordered" className="mt-6 p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-gold-500 mt-0.5" />
          <div className="text-sm text-parchment-200/60">
            <p className="mb-2">
              <strong className="text-parchment-100">Name Extraction</strong> uses
              Claude AI to identify and classify names in Torah verses. This requires
              the Claude CLI to be configured.
            </p>
            <p>
              <strong className="text-parchment-100">Gematria Population</strong>{' '}
              calculates numerical values for each word in the Torah, enabling
              gematria searches.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
