import React, { useEffect, useState } from 'react';
import type { HealthStatus } from '../types';
import { api } from '../services/api';
import {
  Settings,
  Cpu,
  Database,
  Globe,
  BookOpen,
  Lock,
  RefreshCw,
  Activity,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = () => {
    setLoading(true);
    api
      .getHealth()
      .then((res) => {
        setHealth(res);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Settings className="w-6 h-6 text-cyan-400" /> Platform Diagnostics & Settings
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            System health, active machine learning model metadata, security feeds, and privacy settings.
          </p>
        </div>

        <button
          onClick={fetchHealth}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white text-xs font-semibold self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Diagnostics</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs">
          Error retrieving telemetry: {error}
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 gap-3">
          <Activity className="w-6 h-6 text-cyan-400 animate-spin" />
          <span className="text-xs font-mono text-slate-500">Checking system diagnostics...</span>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Service Health Telemetry Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* ML Engine Card */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-cyan-400" /> Machine Learning Engine
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40 font-bold">
                  {health?.machine_learning?.status?.toUpperCase()}
                </span>
              </div>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Model Algorithm:</span>
                  <span className="text-white font-bold">{health?.machine_learning?.model_type || 'Random Forest'}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Model Version:</span>
                  <span className="text-slate-200">{health?.machine_learning?.model_version || 'v1.0.0'}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">URL-Only Features:</span>
                  <span className="text-cyan-400 font-bold">{health?.machine_learning?.features_loaded || 22}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">SHAP TreeExplainer:</span>
                  <span className="text-emerald-400 font-bold">
                    {health?.machine_learning?.shap_explainer_loaded ? 'Ready' : 'Fallback'}
                  </span>
                </div>
              </div>
            </div>

            {/* Persistence & Database Card */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Database className="w-4 h-4 text-cyan-400" /> Persistence & Storage
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40 font-bold">
                  {health?.database?.status?.toUpperCase()}
                </span>
              </div>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Storage Backend:</span>
                  <span className="text-white font-bold">SQLite / PostgreSQL</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">ORM Layer:</span>
                  <span className="text-slate-200">SQLAlchemy 2.0 (Async)</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Data Retention:</span>
                  <span className="text-slate-200">90 Days (Configurable)</span>
                </div>
              </div>
            </div>

            {/* External Threat Feeds Card */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Globe className="w-4 h-4 text-cyan-400" /> Threat Intelligence Integrations
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-400 border border-slate-700 font-bold">
                  ACTIVE
                </span>
              </div>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Google Safe Browsing:</span>
                  <span className="text-slate-300">{health?.threat_intelligence?.google_safe_browsing}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">PhishTank Feed:</span>
                  <span className="text-slate-300">{health?.threat_intelligence?.phishtank}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">OpenPhish Stream:</span>
                  <span className="text-slate-300">{health?.threat_intelligence?.openphish}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Safe DNS Resolution:</span>
                  <span className="text-emerald-400">{health?.threat_intelligence?.live_dns_resolution}</span>
                </div>
              </div>
            </div>

            {/* RAG Knowledge Base Card */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-cyan-400" /> RAG Knowledge Base
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40 font-bold">
                  {health?.rag_knowledge_base?.status?.toUpperCase()}
                </span>
              </div>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Indexed Guidance Chunks:</span>
                  <span className="text-cyan-400 font-bold">{health?.rag_knowledge_base?.chunks_indexed || 11}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Authority Sources:</span>
                  <span className="text-slate-200">CISA, OWASP, NIST</span>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy & Operational Security Policies */}
          <div className="cyber-card rounded-xl p-6 border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold tracking-wider text-slate-300 uppercase flex items-center gap-2">
              <Lock className="w-4 h-4 text-cyan-400" /> Privacy, Security, & Secret Handling
            </h3>
            <div className="text-xs text-slate-400 space-y-2 leading-relaxed">
              <p>
                • <strong>Zero Credential Storage:</strong> FraudLens AI never stores passwords, user sessions, or personal credentials.
              </p>
              <p>
                • <strong>Strict SSRF Mitigation:</strong> All external DNS lookups revalidate resolved IP addresses against RFC 1918, loopback, link-local, and cloud metadata CIDR blocks to prevent Server-Side Request Forgery.
              </p>
              <p>
                • <strong>Secret Isolation:</strong> Threat intelligence API keys and LLM tokens are kept exclusively in server-side environment variables and are never transmitted to the frontend client.
              </p>
              <p>
                • <strong>Safe Pre-Render Evaluation:</strong> Target URLs are inspected structurally without rendering untrusted DOM elements or executing client scripts.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
