import React from 'react';
import type { ServerLocation } from '../types';
import { Globe, MapPin, Network, Server, Shield } from 'lucide-react';

interface ServerLocationCardProps {
  location?: ServerLocation;
  primaryIp?: string;
}

export const ServerLocationCard: React.FC<ServerLocationCardProps> = ({ location, primaryIp }) => {
  const ip = location?.ip || primaryIp || 'Not Resolved';
  const country = location?.country || 'Unknown';
  const city = location?.city || 'Unknown';
  const region = location?.region || 'Unknown';
  const isp = location?.isp || 'Unknown';
  const org = location?.org || location?.as_number || 'Unknown';
  const coords =
    location?.latitude && location?.longitude
      ? `${location.latitude.toFixed(4)}°, ${location.longitude.toFixed(4)}°`
      : 'Unavailable';

  return (
    <div className="cyber-card rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <Globe className="w-4 h-4 text-cyan-400" /> Server Location & Host
        </h3>
        <span className="text-xs px-2 py-0.5 rounded bg-cyan-950/40 text-cyan-400 border border-cyan-800/40 font-mono">
          {country}
        </span>
      </div>

      {/* Mini Visual World Representation */}
      <div className="h-24 w-full rounded-lg bg-slate-950/80 border border-slate-800/80 relative overflow-hidden flex items-center justify-center mb-4">
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:12px_12px] opacity-60" />
        <div className="relative z-10 flex flex-col items-center text-center">
          <div className="w-3 h-3 rounded-full bg-cyan-400 animate-ping absolute -top-1" />
          <div className="w-3 h-3 rounded-full bg-cyan-400 border-2 border-slate-900 mb-1" />
          <span className="text-xs font-bold text-slate-200">
            {city !== 'Unknown' ? `${city}, ${country}` : country}
          </span>
          <span className="text-[10px] text-slate-500 font-mono">{coords}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/60">
          <span className="text-slate-500 block mb-0.5 flex items-center gap-1">
            <Server className="w-3 h-3 text-slate-400" /> Resolved IP
          </span>
          <span className="font-mono text-cyan-300 font-semibold truncate block" title={ip}>
            {ip}
          </span>
        </div>

        <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/60">
          <span className="text-slate-500 block mb-0.5 flex items-center gap-1">
            <MapPin className="w-3 h-3 text-slate-400" /> Region / State
          </span>
          <span className="font-mono text-slate-200 font-semibold truncate block" title={region}>
            {region}
          </span>
        </div>

        <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/60">
          <span className="text-slate-500 block mb-0.5 flex items-center gap-1">
            <Network className="w-3 h-3 text-slate-400" /> Network ISP
          </span>
          <span className="font-mono text-slate-200 truncate block" title={isp}>
            {isp}
          </span>
        </div>

        <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800/60">
          <span className="text-slate-500 block mb-0.5 flex items-center gap-1">
            <Shield className="w-3 h-3 text-slate-400" /> ASN / Org
          </span>
          <span className="font-mono text-slate-200 truncate block" title={org}>
            {org}
          </span>
        </div>
      </div>
    </div>
  );
};
