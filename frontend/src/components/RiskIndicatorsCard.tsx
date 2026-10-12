import React from 'react';
import type { RiskIndicator } from '../types';
import { AlertCircle, AlertTriangle, ShieldCheck } from 'lucide-react';

interface RiskIndicatorsCardProps {
  indicators?: RiskIndicator[];
}

export const RiskIndicatorsCard: React.FC<RiskIndicatorsCardProps> = ({ indicators = [] }) => {
  if (!indicators || indicators.length === 0) {
    return (
      <div className="cyber-card rounded-xl p-5 border border-slate-800">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-3 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" /> Risk Indicators
        </h3>
        <div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-900/30 text-emerald-300 text-sm flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>No anomalous risk heuristics or threat-intelligence triggers were flagged for this URL.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="cyber-card rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400" /> Risk Indicators ({indicators.length})
        </h3>
        <span className="text-xs text-slate-500 font-mono">Automated Signals</span>
      </div>

      <div className="space-y-3">
        {indicators.map((ind, idx) => {
          const isCritical = ind.severity === 'CRITICAL' || ind.severity === 'HIGH';
          return (
            <div
              key={idx}
              className={`p-3.5 rounded-lg border transition-all ${
                isCritical
                  ? 'bg-rose-950/20 border-rose-900/40 hover:border-rose-700/60'
                  : 'bg-amber-950/20 border-amber-900/40 hover:border-amber-700/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span
                  className={`text-sm font-bold flex items-center gap-1.5 ${
                    isCritical ? 'text-rose-300' : 'text-amber-300'
                  }`}
                >
                  {isCritical ? (
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  )}
                  {ind.title}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${
                    isCritical
                      ? 'bg-rose-900/40 text-rose-300 border-rose-700/50'
                      : 'bg-amber-900/40 text-amber-300 border-amber-700/50'
                  }`}
                >
                  {ind.severity}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed mt-1">
                {ind.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
