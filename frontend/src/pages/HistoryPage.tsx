import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { ScanResult } from '../types';
import { api } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import {
  History,
  Search,
  Filter,
  Trash2,
  Activity,
  Layers,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const [limit] = useState(15);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadScans = () => {
    setLoading(true);
    api
      .listScans(search, riskFilter, limit, page * limit)
      .then((data) => {
        setScans(data.items);
        setTotal(data.total);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadScans();
  }, [search, riskFilter, page]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Delete this scan record permanently?')) return;
    try {
      await api.deleteScan(id);
      loadScans();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  const riskFilters = ['ALL', 'HIGH', 'MEDIUM', 'LOW', 'INCONCLUSIVE'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-cyan-400" /> Scan Audit History
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse, search, and audit past phishing analysis evaluations.
          </p>
        </div>

        <button
          onClick={loadScans}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white text-xs font-semibold self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Search and Filters Bar */}
      <div className="cyber-card rounded-xl p-4 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            placeholder="Search by URL or domain keyword..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          <span className="text-xs text-slate-500 mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Risk:
          </span>
          {riskFilters.map((rf) => (
            <button
              key={rf}
              onClick={() => {
                setRiskFilter(rf);
                setPage(0);
              }}
              className={`px-2.5 py-1 rounded-md text-xs font-mono font-semibold transition-all cursor-pointer ${
                riskFilter === rf
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {rf}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs">
          Error retrieving scan history: {error}
        </div>
      )}

      {/* Table */}
      <div className="cyber-card rounded-xl border border-slate-800 overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-16 gap-3">
            <Activity className="w-6 h-6 text-cyan-400 animate-spin" />
            <span className="text-xs font-mono text-slate-500">Querying scan records...</span>
          </div>
        ) : scans.length === 0 ? (
          <div className="text-center p-16 space-y-3">
            <Layers className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-sm font-bold text-white">No Matching Scans Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No historical records matched your search parameters. Try adjusting filters or scanning a new URL.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-500 uppercase font-mono text-[10px]">
                  <th className="py-3 px-4">Target URL</th>
                  <th className="py-3 px-4">Risk Level</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Model Probability</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {scans.map((scan) => (
                  <tr key={scan.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-medium text-slate-200 max-w-md truncate" title={scan.url}>
                      {scan.url}
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge level={scan.risk_level} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-200">
                      {scan.risk_score} / 100
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {scan.model_score !== null && scan.model_score !== undefined
                        ? `${(scan.model_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 font-mono text-[11px]">
                      {new Date(scan.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/scan/${scan.id}`}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 font-semibold text-xs transition-colors"
                        >
                          Report
                        </Link>
                        <button
                          onClick={(e) => handleDelete(scan.id, e)}
                          className="p-1 rounded text-slate-500 hover:text-rose-400 transition-colors cursor-pointer"
                          title="Delete record"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {total > limit && (
          <div className="flex items-center justify-between p-4 border-t border-slate-800 bg-slate-950/40 text-xs font-mono text-slate-400">
            <span>
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total} records
            </span>
            <div className="flex items-center gap-1">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="p-1.5 rounded border border-slate-800 bg-slate-900 disabled:opacity-40 cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-2 font-bold text-white">Page {page + 1}</span>
              <button
                disabled={(page + 1) * limit >= total}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded border border-slate-800 bg-slate-900 disabled:opacity-40 cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
