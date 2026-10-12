import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Search, Cpu, Globe, Lock, AlertTriangle } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const [urlInput, setUrlInput] = useState('');
  const navigate = useNavigate();

  const handleScanSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) return;
    navigate(`/scan?url=${encodeURIComponent(urlInput.trim())}`);
  };

  const sampleTargets = [
    { label: 'Legitimate: GitHub', url: 'https://www.github.com' },
    { label: 'Legitimate: Wikipedia', url: 'https://www.wikipedia.org' },
    { label: 'Phishing: Spoofed PayPal', url: 'http://secure-login-update-paypal-verification.com/account/login?token=abc' },
    { label: 'Suspicious: Raw IP Literal', url: 'http://192.168.1.1/admin/login.php' },
  ];

  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto px-4 space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-800/60 bg-cyan-950/30 text-cyan-400 text-xs font-mono font-semibold tracking-wide">
          <Shield className="w-3.5 h-3.5" />
          <span>CYBERSECURITY RISK ANALYSIS PLATFORM</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Intelligent Phishing Detection &{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500 bg-clip-text text-transparent">
            Website Risk Analysis
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          FraudLens AI extracts structural URL features, runs machine learning trained on 235,000+ benchmark URLs,
          calculates mathematical SHAP explainability, and queries external security evidence without executing untrusted code.
        </p>

        {/* Hero Scanner Form */}
        <div className="max-w-2xl mx-auto mt-8">
          <form onSubmit={handleScanSubmit} className="relative flex items-center">
            <input
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="Enter suspicious URL to inspect (e.g., https://example.com/login)..."
              className="w-full pl-4 pr-32 py-4 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 text-sm shadow-xl font-mono"
            />
            <button
              type="submit"
              className="absolute right-2 top-2 bottom-2 px-6 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-md transition-all cursor-pointer"
            >
              <Search className="w-4 h-4" />
              <span>Inspect</span>
            </button>
          </form>

          {/* Quick Target Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 mt-4 text-xs">
            <span className="text-slate-500">Quick Test Targets:</span>
            {sampleTargets.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setUrlInput(item.url)}
                className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-400 hover:border-slate-700 font-mono transition-all text-[11px]"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* 3 Core Architecture Pillars */}
      <section className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="cyber-card rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white">Machine Learning Classification</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Trained and evaluated on the official UCI PhiUSIIL dataset (235,795 URLs).
            Evaluates 22 URL-only structural features with zero test set contamination.
          </p>
          <div className="pt-2 text-xs font-mono text-cyan-400 flex items-center gap-1">
            <span>Random Forest & XGBoost Benchmarked</span>
          </div>
        </div>

        <div className="cyber-card rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-950/80 border border-blue-800/40 flex items-center justify-center text-blue-400">
            <Globe className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white">Domain & SSRF Defense</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Safe DNS querying and TLS handshake analysis with strict SSRF controls.
            Blocks loopback, RFC 1918 private subnets, and cloud metadata destinations.
          </p>
          <div className="pt-2 text-xs font-mono text-blue-400 flex items-center gap-1">
            <span>DNS-Rebinding Protection Active</span>
          </div>
        </div>

        <div className="cyber-card rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-950/80 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white">Explainable AI & RAG Assistant</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Mathematical SHAP feature attribution translates model decisions into plain English.
            RAG cybersecurity assistant answers scan questions grounded in CISA, OWASP, and NIST guidelines.
          </p>
          <div className="pt-2 text-xs font-mono text-emerald-400 flex items-center gap-1">
            <span>TreeSHAP + Trusted Knowledge</span>
          </div>
        </div>
      </section>

      {/* Workflow Explanation */}
      <section className="max-w-5xl mx-auto px-4 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8">
        <h2 className="text-xl font-bold text-white mb-2 text-center">Multi-Agent LangGraph Workflow</h2>
        <p className="text-xs text-slate-400 text-center max-w-xl mx-auto mb-8">
          Deterministic tools and specialized agents collaborate through a typed LangGraph state machine.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 text-xs font-mono">
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center space-y-1">
            <span className="w-6 h-6 rounded-full bg-cyan-950 text-cyan-400 font-bold inline-flex items-center justify-center mb-1">
              1
            </span>
            <div className="font-bold text-slate-200">URL Analysis</div>
            <div className="text-[11px] text-slate-400">Scheme filter & 22 lexical features</div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center space-y-1">
            <span className="w-6 h-6 rounded-full bg-cyan-950 text-cyan-400 font-bold inline-flex items-center justify-center mb-1">
              2
            </span>
            <div className="font-bold text-slate-200">Domain Intel</div>
            <div className="text-[11px] text-slate-400">DNS records & TLS handshake</div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center space-y-1">
            <span className="w-6 h-6 rounded-full bg-cyan-950 text-cyan-400 font-bold inline-flex items-center justify-center mb-1">
              3
            </span>
            <div className="font-bold text-slate-200">ML Inference</div>
            <div className="text-[11px] text-slate-400">Model score & SHAP attribution</div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center space-y-1">
            <span className="w-6 h-6 rounded-full bg-cyan-950 text-cyan-400 font-bold inline-flex items-center justify-center mb-1">
              4
            </span>
            <div className="font-bold text-slate-200">Risk Engine</div>
            <div className="text-[11px] text-slate-400">Deterministic rule synthesis</div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center space-y-1">
            <span className="w-6 h-6 rounded-full bg-cyan-950 text-cyan-400 font-bold inline-flex items-center justify-center mb-1">
              5
            </span>
            <div className="font-bold text-slate-200">Explanation</div>
            <div className="text-[11px] text-slate-400">Grounded advice & remediation</div>
          </div>
        </div>
      </section>

      {/* Responsible-Use Disclaimer */}
      <section className="max-w-3xl mx-auto px-4 text-center">
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-500 leading-relaxed space-y-1">
          <div className="flex items-center justify-center gap-1.5 font-bold text-slate-400 uppercase tracking-wide">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Responsible-Use & Operational Disclaimer</span>
          </div>
          <p>
            FraudLens AI provides evidence-based risk assessment derived from statistical URL patterns,
            machine learning models, and security feeds. Automated detection does not guarantee complete security or proof of malicious intent.
            Never visit untrusted URLs directly from an unshielded workstation.
          </p>
        </div>
      </section>
    </div>
  );
};
