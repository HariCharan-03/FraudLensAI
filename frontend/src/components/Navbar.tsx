import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, LayoutDashboard, Search, History, Bot, Settings } from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    api
      .getHealth()
      .then((res) => setIsHealthy(res.status === 'healthy'))
      .catch(() => setIsHealthy(false));
  }, [location.pathname]);

  const navLinks = [
    { to: '/', label: 'Overview', icon: Shield },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/scan', label: 'URL Scanner', icon: Search },
    { to: '/history', label: 'Scan History', icon: History },
    { to: '/assistant', label: 'AI Assistant', icon: Bot },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all">
              <Shield className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  FraudLens AI
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/40">
                  v1.0
                </span>
              </div>
              <span className="text-[10px] text-slate-400 tracking-wider uppercase block">
                Phishing Risk Intelligence
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-slate-800 text-cyan-400 border border-slate-700/80 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right Section: System Status & Scan Button */}
          <div className="flex items-center gap-3">
            {/* Live Health Status Indicator */}
            <div
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-slate-800 bg-slate-900/60 text-[11px] font-mono"
              title={isHealthy ? 'Backend & ML Online' : 'Backend Connecting'}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isHealthy === true
                    ? 'bg-emerald-400 animate-pulse'
                    : isHealthy === false
                    ? 'bg-rose-400'
                    : 'bg-amber-400'
                }`}
              />
              <span className="text-slate-400">
                {isHealthy === true ? 'SYSTEM READY' : isHealthy === false ? 'OFFLINE' : 'CHECKING'}
              </span>
            </div>

            <Link
              to="/scan"
              className="flex items-center gap-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold px-3.5 py-2 rounded-lg text-xs shadow-md shadow-cyan-500/20 transition-all"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Scan URL</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};
