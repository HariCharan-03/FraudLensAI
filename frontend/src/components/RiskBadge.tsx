import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, HelpCircle } from 'lucide-react';

interface RiskBadgeProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'INCONCLUSIVE';
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-sm px-3 py-1 gap-1.5',
    lg: 'text-base px-4 py-1.5 gap-2 font-bold tracking-wide',
  };

  const config = {
    LOW: {
      label: 'LOW RISK',
      bg: 'bg-emerald-950/60 text-emerald-400 border-emerald-500/40 shadow-emerald-950/50',
      icon: ShieldCheck,
    },
    MEDIUM: {
      label: 'MEDIUM RISK',
      bg: 'bg-amber-950/60 text-amber-400 border-amber-500/40 shadow-amber-950/50',
      icon: AlertTriangle,
    },
    HIGH: {
      label: 'HIGH RISK',
      bg: 'bg-rose-950/60 text-rose-400 border-rose-500/50 shadow-rose-950/50 animate-pulse',
      icon: ShieldAlert,
    },
    INCONCLUSIVE: {
      label: 'INCONCLUSIVE',
      bg: 'bg-slate-900/60 text-slate-400 border-slate-700 shadow-slate-950/50',
      icon: HelpCircle,
    },
  }[level] || {
    label: level,
    bg: 'bg-slate-900 text-slate-400 border-slate-700',
    icon: HelpCircle,
  };

  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-sm font-semibold uppercase ${sizeClasses[size]} ${config.bg}`}
    >
      <Icon className={size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />
      {config.label}
    </span>
  );
};
