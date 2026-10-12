import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import {
  Search,
  Lock,
  AlertTriangle,
  Activity,
  CheckCircle2,
} from 'lucide-react';

export const ScannerPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [url, setUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const scanSteps = [
    { title: 'Validating URL Scheme & SSRF Protection', desc: 'Ensuring HTTP/HTTPS and blocking private subnets' },
    { title: 'Extracting 22 URL-Only Lexical Features', desc: 'Entropy, obfuscation ratio, TLD legitimacy priors' },
    { title: 'Running ML Classifier & SHAP Attributions', desc: 'Random Forest inference trained on 235k PhiUSIIL URLs' },
    { title: 'Safe Domain & TLS Handshake Inspection', desc: 'Querying DNS records and TLS certificate without code execution' },
    { title: 'Deterministic Risk Engine Synthesis', desc: 'Combining model probability, domain heuristics, and threat feeds' },
  ];

  useEffect(() => {
    const prefill = searchParams.get('url');
    if (prefill) {
      setUrl(prefill);
      runScan(prefill);
    }
  }, [searchParams]);

  const runScan = async (targetUrl: string) => {
    const cleanUrl = targetUrl.trim();
    if (!cleanUrl) {
      setError('Please provide a valid URL string.');
      return;
    }

    setError(null);
    setScanning(true);
    setCurrentStep(0);

    // Step simulation for transparency
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < scanSteps.length - 1 ? prev + 1 : prev));
    }, 600);

    try {
      const result = await api.submitScan(cleanUrl);
      clearInterval(stepInterval);
      navigate(`/scan/${result.id}`);
    } catch (err: any) {
      clearInterval(stepInterval);
      setError(err.message || 'Scanning failed. Please check the URL format.');
    } finally {
      setScanning(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runScan(url);
  };

  const sampleTargets = [
    {
      category: 'Benign Website',
      name: 'Google',
      url: 'https://www.google.com',
      badge: 'Legitimate Profile',
    },
    {
      category: 'Benign Website',
      name: 'GitHub',
      url: 'https://www.github.com',
      badge: 'Legitimate Profile',
    },
    {
      category: 'Spoofed Phishing',
      name: 'PayPal Phish',
      url: 'http://secure-login-update-paypal-verification.com/account/login?token=abc',
      badge: 'Brand Keywords & No HTTPS',
    },
    {
      category: 'Suspicious Infrastructure',
      name: 'Raw IP Host',
      url: 'http://192.168.1.1/admin/login.php',
      badge: 'IP Literal Host',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center justify-center gap-2.5">
          <Search className="w-7 h-7 text-cyan-400" />
          <span>Real-Time Phishing & Risk Scanner</span>
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          Analyze any website URL. Extracted features are passed to our trained machine learning
          model and verified against security intelligence without loading arbitrary webpage payloads.
        </p>
      </div>

      {/* Main Scanner Box */}
      <div className="cyber-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider block">
              Website Target URL
            </label>
            <div className="relative">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={scanning}
                placeholder="https://example-domain.com/secure/login"
                className="w-full px-4 py-3.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 font-mono text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 disabled:opacity-50"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
            <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-cyan-400" />
              <span>Safe analysis: Never fetches or renders untrusted HTML bodies.</span>
            </div>

            <button
              type="submit"
              disabled={scanning || !url.trim()}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition-all cursor-pointer"
            >
              {scanning ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  <span>Scanning Target...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Execute Security Scan</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Live Step Progress Indicator */}
        {scanning && (
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4 animate-spin text-cyan-400" /> Multi-Agent Orchestration in Progress
              </span>
              <span className="text-xs font-mono text-slate-400">
                Step {currentStep + 1} of {scanSteps.length}
              </span>
            </div>

            <div className="space-y-2">
              {scanSteps.map((step, idx) => {
                const isDone = idx < currentStep;
                const isCurrent = idx === currentStep;
                return (
                  <div
                    key={idx}
                    className={`flex items-start gap-3 p-2.5 rounded-lg text-xs transition-all ${
                      isCurrent
                        ? 'bg-cyan-950/40 border border-cyan-800/40 text-cyan-200'
                        : isDone
                        ? 'text-slate-300'
                        : 'text-slate-600 opacity-60'
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    ) : isCurrent ? (
                      <Activity className="w-4 h-4 text-cyan-400 animate-spin shrink-0 mt-0.5" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="font-semibold">{step.title}</div>
                      <div className="text-[11px] text-slate-400">{step.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Preset Target Cards */}
      <div className="space-y-3">
        <h3 className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
          Quick Test Target Presets
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {sampleTargets.map((sample, idx) => (
            <div
              key={idx}
              onClick={() => {
                setUrl(sample.url);
                runScan(sample.url);
              }}
              className="cyber-card rounded-xl p-3.5 border border-slate-800 hover:border-slate-700 cursor-pointer transition-all group"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-white group-hover:text-cyan-400 transition-colors">
                  {sample.name}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                  {sample.badge}
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-400 truncate">{sample.url}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
