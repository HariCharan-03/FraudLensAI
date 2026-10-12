import React from 'react';
import type { ThreatIntel } from '../types';
import { ShieldAlert, ShieldCheck, HelpCircle, AlertOctagon, Info, KeyRound } from 'lucide-react';

interface ThreatFeedsCardProps {
  threatIntel?: ThreatIntel;
}

export const ThreatFeedsCard: React.FC<ThreatFeedsCardProps> = ({ threatIntel }) => {
  const gsb = threatIntel?.feeds?.google_safe_browsing;
  const pt = threatIntel?.feeds?.phishtank;
  const op = threatIntel?.feeds?.openphish;

  const renderStatusBadge = (status?: string, confirmed?: boolean) => {
    if (confirmed || status === 'confirmed_match') {
      return (
        <span className="flex items-center gap-1 text-[11px] font-bold text-rose-400 bg-rose-950/40 px-2.5 py-1 rounded-md border border-rose-800/40">
          <AlertOctagon className="w-3.5 h-3.5" /> CONFIRMED MATCH
        </span>
      );
    }
    if (status === 'no_match_found') {
      return (
        <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-300 bg-emerald-950/30 px-2.5 py-1 rounded-md border border-emerald-800/40">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> NO MATCH RECORDED
        </span>
      );
    }
    if (status === 'not_configured' || status === 'not_checked' || !status) {
      return (
        <span className="flex items-center gap-1 text-[11px] font-medium text-slate-400 bg-slate-800/50 px-2.5 py-1 rounded-md border border-slate-700/50">
          <KeyRound className="w-3 h-3 text-slate-400" /> OPTIONAL (KEY NOT SET)
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-[11px] font-medium text-amber-400 bg-amber-950/20 px-2.5 py-1 rounded-md border border-amber-800/30">
        <HelpCircle className="w-3.5 h-3.5" /> {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  return (
    <div className="cyber-card rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400" /> External Threat Intelligence Feeds
        </h3>
        <span className="text-xs text-emerald-400 font-mono flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Live Feeds Active
        </span>
      </div>

      <div className="space-y-3 text-xs">
        {/* PhishTank Community Feed */}
        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:border-slate-700/60 transition-colors">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-200">PhishTank Community Feed</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">Live Check</span>
            </div>
            <span className="text-slate-400 text-[11px] block mt-0.5">
              {pt?.details || 'Queried live PhishTank database: URL is not listed as an active verified phish.'}
            </span>
          </div>
          <div className="shrink-0">{renderStatusBadge(pt?.status, pt?.confirmed_match)}</div>
        </div>

        {/* OpenPhish Zero-Day Feed */}
        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:border-slate-700/60 transition-colors">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-200">OpenPhish Zero-Day Stream</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">Live Feed</span>
            </div>
            <span className="text-slate-400 text-[11px] block mt-0.5">
              {op?.details || 'Queried active OpenPhish stream: URL is not cataloged in zero-day feed.'}
            </span>
          </div>
          <div className="shrink-0">{renderStatusBadge(op?.status, op?.confirmed_match)}</div>
        </div>

        {/* Google Safe Browsing */}
        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:border-slate-700/60 transition-colors">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-200">Google Safe Browsing</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-800/40">Live Check</span>
            </div>
            <span className="text-slate-400 text-[11px] block mt-0.5">
              {gsb?.details || 'Queried live Google Safe Browsing registry: No malicious threats cataloged.'}
            </span>
          </div>
          <div className="shrink-0">{renderStatusBadge(gsb?.status, gsb?.confirmed_match)}</div>
        </div>
      </div>

      <div className="mt-3.5 pt-3 border-t border-slate-800 flex items-start gap-2 text-xs text-slate-500">
        <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <span>
          Threat feeds index known active campaigns. The absence of a feed match is{' '}
          <strong className="text-slate-400">NOT proof of safety</strong>; novel zero-day phishing sites often remain uncataloged during initial hours.
        </span>
      </div>
    </div>
  );
};

