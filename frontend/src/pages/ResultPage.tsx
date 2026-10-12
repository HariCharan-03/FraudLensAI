import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import type { ScanResult } from '../types';
import { api } from '../services/api';
import { RiskGauge } from '../components/RiskGauge';
import { RiskIndicatorsCard } from '../components/RiskIndicatorsCard';
import { FeatureImportanceChart } from '../components/FeatureImportanceChart';
import { ServerLocationCard } from '../components/ServerLocationCard';
import { DnsRecordsCard } from '../components/DnsRecordsCard';
import { ThreatFeedsCard } from '../components/ThreatFeedsCard';
import { SafetyRecommendations } from '../components/SafetyRecommendations';
import {
  ArrowLeft,
  Download,
  Bot,
  Shield,
  Activity,
  Check,
  Copy,
  Clock,
  Fingerprint,
} from 'lucide-react';

export const ResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api
      .getScan(id)
      .then((data) => {
        setScan(data);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const copyReport = () => {
    if (!scan) return;
    const summary = `FRAUDLENS AI SECURITY REPORT\nTarget: ${scan.url}\nRisk Assessment: ${scan.risk_level} (${scan.risk_score}/100)\nModel Phishing Likelihood: ${
      scan.model_score !== null && scan.model_score !== undefined ? (scan.model_score * 100).toFixed(1) + '%' : 'N/A'
    }\nScan ID: ${scan.id}\nTimestamp: ${new Date(scan.created_at).toUTCString()}`;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const exportJson = () => {
    if (!scan) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(scan, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `fraudlens_report_${scan.id.slice(0, 8)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Activity className="w-8 h-8 text-cyan-400 animate-spin" />
        <span className="text-xs font-mono text-slate-400">Loading forensic scan report...</span>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="max-w-xl mx-auto my-16 cyber-card p-8 rounded-2xl text-center space-y-4">
        <Shield className="w-10 h-10 text-rose-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Scan Record Not Found</h2>
        <p className="text-xs text-slate-400">{error || 'Unable to locate this scan record.'}</p>
        <Link
          to="/scan"
          className="inline-block px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 font-bold text-xs"
        >
          Return to Scanner
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/scan')}
            className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition-all cursor-pointer"
            title="Back to Scanner"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-white tracking-tight">Security Forensic Report</h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40 font-semibold uppercase">
                {scan.status}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-500 mt-1">
              <span className="flex items-center gap-1">
                <Fingerprint className="w-3 h-3 text-slate-600" /> ID: {scan.id.slice(0, 18)}...
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-600" /> {new Date(scan.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Right Actions: Export, Copy, Ask Assistant */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={copyReport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white text-xs font-semibold transition-all cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={exportJson}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white text-xs font-semibold transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export Report</span>
          </button>

          <Link
            to={`/assistant?scanId=${scan.id}`}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 transition-all"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Ask AI Assistant</span>
          </Link>
        </div>
      </div>

      {/* Target URL Cyber Banner */}
      <div className="cyber-card rounded-xl p-4 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 shrink-0 font-mono font-bold text-xs">
            URL
          </div>
          <div className="overflow-hidden">
            <span className="font-mono text-sm sm:text-base font-bold text-white truncate block">
              {scan.url}
            </span>
            <span className="text-[11px] font-mono text-slate-500 truncate block">
              Normalized: {scan.normalized_url || scan.url}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <span className="text-xs font-mono text-slate-400">
            Model P(Phish):{' '}
            <strong className="text-white">
              {scan.model_score !== null && scan.model_score !== undefined
                ? `${(scan.model_score * 100).toFixed(1)}%`
                : 'N/A'}
            </strong>
          </span>
        </div>
      </div>

      {/* Flagship 3-Column Forensic Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Risk Gauge + Risk Indicators (Width 4/12) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Circular Risk Meter Card */}
          <div className="cyber-card rounded-xl p-6 border border-slate-800 flex flex-col items-center text-center">
            <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest mb-4">
              Composite Risk Score
            </span>
            <RiskGauge score={scan.risk_score} level={scan.risk_level} size={190} />
            <p className="text-xs text-slate-400 mt-4 leading-relaxed max-w-xs">
              {scan.plain_explanation || 'Comprehensive risk score synthesized from ML and security evidence.'}
            </p>
          </div>

          {/* Risk Indicators Card */}
          <RiskIndicatorsCard indicators={scan.indicators} />
        </div>

        {/* Middle Column: Server Location + DNS & TLS (Width 4/12) */}
        <div className="lg:col-span-4 space-y-6">
          <ServerLocationCard
            location={scan.domain_intel?.server_location}
            primaryIp={scan.domain_intel?.primary_ip}
          />

          <DnsRecordsCard
            dnsRecords={scan.domain_intel?.dns_records}
            dnsStatus={scan.domain_intel?.dns_status}
            sslCertificate={scan.domain_intel?.ssl_certificate}
          />
        </div>

        {/* Right Column: SHAP Explainability + Threat Feeds + Safety Advice (Width 4/12) */}
        <div className="lg:col-span-4 space-y-6">
          <FeatureImportanceChart
            explanations={scan.feature_explanations}
            modelType={scan.model_type}
          />

          <ThreatFeedsCard threatIntel={scan.threat_intel} />

          <SafetyRecommendations
            recommendations={scan.recommendations}
            riskLevel={scan.risk_level}
          />
        </div>
      </div>
    </div>
  );
};
