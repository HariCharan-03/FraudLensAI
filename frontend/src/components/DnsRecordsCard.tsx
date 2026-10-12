import React, { useState } from 'react';
import type { DnsRecords, SslCertificate } from '../types';
import { Database, Lock, CheckCircle2, XCircle } from 'lucide-react';

interface DnsRecordsCardProps {
  dnsRecords?: DnsRecords;
  dnsStatus?: string;
  sslCertificate?: SslCertificate;
}

export const DnsRecordsCard: React.FC<DnsRecordsCardProps> = ({
  dnsRecords,
  dnsStatus = 'no_records',
  sslCertificate,
}) => {
  const [activeTab, setActiveTab] = useState<'A' | 'MX' | 'TXT' | 'SSL'>('A');

  const records = dnsRecords || { A: [], AAAA: [], MX: [], TXT: [], NS: [] };
  const aRecords = [...(records.A || []), ...(records.AAAA || [])];
  const mxRecords = records.MX || [];
  const txtRecords = records.TXT || [];

  return (
    <div className="cyber-card rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" /> DNS Records & TLS
        </h3>
        <span
          className={`text-xs px-2 py-0.5 rounded font-mono ${
            dnsStatus === 'resolved'
              ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-800/40'
              : 'bg-slate-800 text-slate-400'
          }`}
        >
          DNS {dnsStatus}
        </span>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 mb-4 gap-1">
        {(['A', 'MX', 'TXT', 'SSL'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-t-lg transition-all ${
              activeTab === tab
                ? 'bg-slate-800 text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab === 'SSL' ? 'TLS/SSL' : `${tab} Records`}
          </button>
        ))}
      </div>

      <div className="min-h-36 max-h-44 overflow-y-auto">
        {activeTab === 'A' && (
          <div className="space-y-1.5 font-mono text-xs">
            {aRecords.length > 0 ? (
              aRecords.map((r, i) => (
                <div key={i} className="p-2 rounded bg-slate-900/60 border border-slate-800/40 text-slate-300">
                  {r}
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-3">No Address (A/AAAA) records found.</p>
            )}
          </div>
        )}

        {activeTab === 'MX' && (
          <div className="space-y-1.5 font-mono text-xs">
            {mxRecords.length > 0 ? (
              mxRecords.map((r, i) => (
                <div key={i} className="p-2 rounded bg-slate-900/60 border border-slate-800/40 text-slate-300">
                  {r}
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-3">No Mail Exchange (MX) records found.</p>
            )}
          </div>
        )}

        {activeTab === 'TXT' && (
          <div className="space-y-1.5 font-mono text-xs">
            {txtRecords.length > 0 ? (
              txtRecords.map((r, i) => (
                <div key={i} className="p-2 rounded bg-slate-900/60 border border-slate-800/40 text-slate-300 break-all">
                  {r}
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-3">No Text (TXT) records found.</p>
            )}
          </div>
        )}

        {activeTab === 'SSL' && (
          <div className="space-y-2 text-xs">
            {sslCertificate ? (
              <>
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-cyan-400" /> Certificate Issuer:
                  </span>
                  <span className="font-semibold text-slate-200">{sslCertificate.issuer || 'Unknown'}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                  <span className="text-slate-400">Validity Status:</span>
                  <span className="flex items-center gap-1 font-semibold">
                    {sslCertificate.is_expired ? (
                      <span className="text-rose-400 flex items-center gap-1">
                        <XCircle className="w-3.5 h-3.5" /> Expired
                      </span>
                    ) : (
                      <span className="text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Valid
                      </span>
                    )}
                  </span>
                </div>
                {sslCertificate.valid_to && (
                  <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                    <span className="text-slate-400">Valid Until:</span>
                    <span className="text-slate-300 font-mono text-[11px]">{sslCertificate.valid_to}</span>
                  </div>
                )}
                {sslCertificate.tls_version && (
                  <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/40">
                    <span className="text-slate-400">TLS Protocol:</span>
                    <span className="text-cyan-300 font-mono text-[11px]">{sslCertificate.tls_version}</span>
                  </div>
                )}
              </>
            ) : (
              <p className="text-xs text-slate-500 py-3">No TLS/SSL certificate data retrieved.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
