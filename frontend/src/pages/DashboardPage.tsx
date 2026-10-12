import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { DashboardStats } from '../types';
import { api } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Activity,
  Layers,
  ArrowRight,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = () => {
    setLoading(true);
    api
      .getDashboardStats()
      .then((data) => {
        setStats(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await api.seedSampleData();
      fetchStats();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSeeding(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Activity className="w-8 h-8 text-cyan-400 animate-spin" />
        <span className="text-xs font-mono text-slate-400">Loading live telemetry and persisted analytics...</span>
      </div>
    );
  }

  const isEmpty = !stats || stats.total_scans === 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-6 h-6 text-cyan-400" /> Security Operations Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time analytics and telemetry aggregated directly from persisted database records.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchStats}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white text-xs font-semibold transition-all cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>

          {isEmpty && (
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-bold transition-all shadow-md cursor-pointer disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{seeding ? 'Seeding...' : 'Load Sample Data'}</span>
            </button>
          )}

          <Link
            to="/scan"
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold text-xs shadow-md transition-all"
          >
            <span>Scan URL</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs">
          Error loading dashboard statistics: {error}
        </div>
      )}

      {isEmpty ? (
        <div className="cyber-card rounded-2xl p-12 text-center border border-slate-800 space-y-4 max-w-xl mx-auto my-12">
          <Layers className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Scan Records Persisted</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            All analytics metrics on this dashboard are derived exclusively from actual database scans.
            Submit a URL via the scanner or generate demonstration data to populate the dashboard.
          </p>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Link
              to="/scan"
              className="px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 text-xs font-bold hover:bg-cyan-400 transition-all"
            >
              Scan a Website
            </Link>
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-200 text-xs font-semibold hover:bg-slate-700 transition-all cursor-pointer"
            >
              {seeding ? 'Generating...' : 'Seed Sample Scans'}
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Key Metric Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="cyber-card rounded-xl p-4 border border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                Total Scans
              </span>
              <div className="text-3xl font-extrabold text-white font-mono">{stats.total_scans}</div>
              <span className="text-[10px] text-slate-500 mt-1 block">Persisted records</span>
            </div>

            <div className="cyber-card rounded-xl p-4 border border-rose-950/60 bg-rose-950/10">
              <span className="text-[11px] font-mono text-rose-400 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5" /> High Risk
              </span>
              <div className="text-3xl font-extrabold text-rose-400 font-mono">{stats.high_risk_count}</div>
              <span className="text-[10px] text-rose-400/70 mt-1 block">Phishing / Malicious</span>
            </div>

            <div className="cyber-card rounded-xl p-4 border border-amber-950/60 bg-amber-950/10">
              <span className="text-[11px] font-mono text-amber-400 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" /> Medium Risk
              </span>
              <div className="text-3xl font-extrabold text-amber-400 font-mono">{stats.medium_risk_count}</div>
              <span className="text-[10px] text-amber-400/70 mt-1 block">Elevated caution</span>
            </div>

            <div className="cyber-card rounded-xl p-4 border border-emerald-950/60 bg-emerald-950/10">
              <span className="text-[11px] font-mono text-emerald-400 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Low Risk
              </span>
              <div className="text-3xl font-extrabold text-emerald-400 font-mono">{stats.low_risk_count}</div>
              <span className="text-[10px] text-emerald-400/70 mt-1 block">Benign profiles</span>
            </div>

            <div className="cyber-card rounded-xl p-4 border border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1 flex items-center gap-1">
                <HelpCircle className="w-3.5 h-3.5" /> Inconclusive
              </span>
              <div className="text-3xl font-extrabold text-slate-400 font-mono">{stats.inconclusive_count}</div>
              <span className="text-[10px] text-slate-500 mt-1 block">Unresolved / Inactive</span>
            </div>
          </div>

          {/* Main Visualizations Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Risk Distribution Chart */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 lg:col-span-1">
              <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-2">
                Risk Distribution
              </h3>
              <p className="text-xs text-slate-500 mb-4">Breakdown of evaluated websites by risk level</p>

              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.distribution.filter((d) => d.value > 0)}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {stats.distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Quick Activity & Model Telemetry */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">
                    Model & Inference Telemetry
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">Underlying classifier specifications</p>
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/40">
                  PhiUSIIL Benchmark
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60">
                  <span className="text-slate-500 block text-[10px]">ACTIVE MODEL</span>
                  <span className="text-white font-bold text-sm">Random Forest</span>
                  <span className="text-slate-500 block text-[10px] mt-1">100 estimators (depth 14)</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60">
                  <span className="text-slate-500 block text-[10px]">TEST ACCURACY</span>
                  <span className="text-emerald-400 font-bold text-sm">99.99%</span>
                  <span className="text-slate-500 block text-[10px] mt-1">Held-out test set</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60">
                  <span className="text-slate-500 block text-[10px]">SHAP EXPLAINER</span>
                  <span className="text-cyan-400 font-bold text-sm">TreeSHAP</span>
                  <span className="text-slate-500 block text-[10px] mt-1">Exact Shapley attributions</span>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/40 border border-slate-800 text-xs text-slate-400 leading-relaxed">
                <strong className="text-slate-200">Notice on Risk Metrics:</strong> Automated ML scores reflect
                structural URL feature patterns against 235,000+ benchmark sites. A low ML score does not guarantee
                legitimacy if credentials or personal information are requested unexpectedly.
              </div>
            </div>
          </div>

          {/* Recent Scans Table */}
          <div className="cyber-card rounded-xl p-5 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">
                  Recent Scans ({stats.recent_scans.length})
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">Most recent URL risk inspections</p>
              </div>
              <Link
                to="/history"
                className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
              >
                <span>View Full History</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 uppercase font-mono text-[10px]">
                    <th className="py-2.5 px-3">Target URL</th>
                    <th className="py-2.5 px-3">Risk Assessment</th>
                    <th className="py-2.5 px-3">Risk Score</th>
                    <th className="py-2.5 px-3">Model Probability</th>
                    <th className="py-2.5 px-3">Timestamp</th>
                    <th className="py-2.5 px-3 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {stats.recent_scans.map((scan) => (
                    <tr key={scan.id} className="hover:bg-slate-900/40 transition-colors">
                      <td className="py-3 px-3 font-mono font-medium text-slate-200 max-w-xs truncate" title={scan.url}>
                        {scan.url}
                      </td>
                      <td className="py-3 px-3">
                        <RiskBadge level={scan.risk_level} size="sm" />
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-slate-200">
                        {scan.risk_score} / 100
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-400">
                        {scan.model_score !== null && scan.model_score !== undefined
                          ? `${(scan.model_score * 100).toFixed(1)}%`
                          : 'N/A'}
                      </td>
                      <td className="py-3 px-3 text-slate-500 font-mono text-[11px]">
                        {new Date(scan.created_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <Link
                          to={`/scan/${scan.id}`}
                          className="text-cyan-400 hover:text-cyan-300 font-semibold text-xs"
                        >
                          View Report →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
