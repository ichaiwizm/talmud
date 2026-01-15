import { useState, useCallback, useRef, useEffect } from 'react';
import { Network, ZoomIn, ZoomOut, Maximize2, Filter } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';
import { useNavigate } from 'react-router-dom';
import { useGraph } from '../hooks/useApi';
import { Card } from '../components/ui/Card';
import { Select, Button } from '../components/ui';
import { Loading } from '../components/ui/Loading';
import { NAME_TYPE_LABELS } from '../lib/utils';
import type { NameType } from '../api/types';

const TYPE_COLORS: Record<NameType, string> = {
  person: '#1e3a5f',
  deity: '#d4a012',
  place: '#2d4a3e',
  people_group: '#4a3252',
  angel: '#5e3a6e',
  unknown: '#2d2a26',
};

export function GraphPage() {
  const navigate = useNavigate();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const graphRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [minWeight, setMinWeight] = useState(2);
  const [typeFilter, setTypeFilter] = useState<NameType | ''>('');
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const { data: graphData, isLoading } = useGraph({
    min_weight: minWeight,
    name_type: typeFilter || undefined,
  });

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({
          width: rect.width,
          height: Math.max(500, window.innerHeight - 300),
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Prepare graph data for force-graph
  const forceGraphData = graphData
    ? {
        nodes: graphData.nodes.map((node) => ({
          id: node.id,
          label: node.label,
          hebrew: node.hebrew,
          type: node.type,
          occurrences: node.occurrences,
          color: TYPE_COLORS[node.type],
        })),
        links: graphData.edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          weight: edge.weight,
        })),
      }
    : { nodes: [], links: [] };

  const handleNodeClick = useCallback(
    (node: { id: string; label: string }) => {
      navigate(`/names/${encodeURIComponent(node.label)}`);
    },
    [navigate]
  );

  const handleZoomIn = () => {
    if (graphRef.current) {
      const currentZoom = graphRef.current.zoom();
      graphRef.current.zoom(currentZoom * 1.5, 400);
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      const currentZoom = graphRef.current.zoom();
      graphRef.current.zoom(currentZoom / 1.5, 400);
    }
  };

  const handleCenter = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400);
    }
  };

  return (
    <div className="max-w-full mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Network className="w-8 h-8 text-gold-500" />
          <h1 className="display-heading text-3xl text-parchment-50">
            Relationship Graph
          </h1>
        </div>
        <p className="text-parchment-200/60">
          Visualize co-occurrence relationships between names in the Torah
        </p>
      </div>

      {/* Controls */}
      <Card variant="bordered" className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-parchment-200/60">
            <Filter className="w-4 h-4" />
            <span className="text-sm">Filters:</span>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-parchment-200/60">Min connections:</label>
            <Select
              value={String(minWeight)}
              onChange={(e) => setMinWeight(Number(e.target.value))}
              options={[
                { value: '1', label: '1+' },
                { value: '2', label: '2+' },
                { value: '3', label: '3+' },
                { value: '5', label: '5+' },
                { value: '10', label: '10+' },
              ]}
              className="w-20"
            />
          </div>

          <Select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as NameType | '')}
            options={[
              { value: '', label: 'All Types' },
              ...Object.entries(NAME_TYPE_LABELS).map(([value, label]) => ({
                value,
                label,
              })),
            ]}
            className="w-36"
          />

          <div className="flex items-center gap-2 ml-auto">
            <Button variant="ghost" size="sm" onClick={handleZoomIn}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleZoomOut}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleCenter}>
              <Maximize2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 mb-4">
        <span className="text-sm text-parchment-200/50">Legend:</span>
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-parchment-200/60">
              {NAME_TYPE_LABELS[type as NameType]}
            </span>
          </div>
        ))}
      </div>

      {/* Graph */}
      <Card variant="bordered" className="overflow-hidden" ref={containerRef}>
        {isLoading ? (
          <div className="flex items-center justify-center" style={{ height: dimensions.height }}>
            <Loading size="lg" />
          </div>
        ) : forceGraphData.nodes.length === 0 ? (
          <div
            className="flex items-center justify-center text-parchment-200/50"
            style={{ height: dimensions.height }}
          >
            No data to display. Try adjusting the filters.
          </div>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={forceGraphData}
            width={dimensions.width}
            height={dimensions.height}
            backgroundColor="#0f0e0d"
            nodeLabel={(node: any) =>
              `${node.label}${node.hebrew ? ` (${node.hebrew})` : ''}\n${node.occurrences} occurrences`
            }
            nodeColor={(node: any) => node.color}
            nodeRelSize={4}
            nodeVal={(node: any) => Math.sqrt(node.occurrences) * 0.5}
            linkColor={() => 'rgba(212, 160, 18, 0.15)'}
            linkWidth={(link: any) => Math.sqrt(link.weight) * 0.5}
            linkDirectionalParticles={0}
            onNodeClick={handleNodeClick}
            onNodeHover={(node: any) => setSelectedNode(node?.id || null)}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const size = Math.sqrt(node.occurrences) * 0.5 + 4;
              const isSelected = selectedNode === node.id;

              // Node circle
              ctx.beginPath();
              ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
              ctx.fillStyle = isSelected ? '#facc15' : node.color;
              ctx.fill();

              // Label (only at higher zoom)
              if (globalScale > 1.5 || isSelected) {
                ctx.font = `${11 / globalScale}px "Frank Ruhl Libre", serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillStyle = isSelected ? '#facc15' : '#f5f0e8';
                ctx.fillText(node.label, node.x, node.y + size + 2);
              }
            }}
            cooldownTicks={100}
            onEngineStop={() => graphRef.current?.zoomToFit(400)}
          />
        )}
      </Card>

      {/* Stats */}
      {graphData && (
        <div className="mt-4 flex items-center gap-6 text-sm text-parchment-200/50">
          <span>
            <span className="text-gold-500">{graphData.nodes.length}</span> names
          </span>
          <span>
            <span className="text-gold-500">{graphData.edges.length}</span> connections
          </span>
          <span className="text-parchment-200/30">
            Click on a node to view name details
          </span>
        </div>
      )}
    </div>
  );
}
