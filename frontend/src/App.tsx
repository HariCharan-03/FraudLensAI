import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { ScannerPage } from './pages/ScannerPage';
import { ResultPage } from './pages/ResultPage';
import { HistoryPage } from './pages/HistoryPage';
import { AssistantPage } from './pages/AssistantPage';
import { SettingsPage } from './pages/SettingsPage';
import { Shield, ExternalLink } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-[#070b13] text-slate-100 selection:bg-cyan-500 selection:text-slate-950 font-sans">
        <Navbar />

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/scan" element={<ScannerPage />} />
            <Route path="/scan/:id" element={<ResultPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/assistant" element={<AssistantPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-900 bg-slate-950/80 py-8 px-4 sm:px-6 lg:px-8 mt-16 text-xs text-slate-500 font-mono">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-cyan-400" />
              <span className="font-bold text-slate-300">FraudLens AI</span>
              <span>— Intelligent Phishing Detection & Website Risk Analysis</span>
            </div>

            <div className="flex items-center gap-6">
              <Link to="/settings" className="hover:text-slate-300 transition-colors">
                Diagnostics
              </Link>
              <Link to="/dashboard" className="hover:text-slate-300 transition-colors">
                Telemetry
              </Link>
              <a
                href="https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+website+dataset"
                target="_blank"
                rel="noreferrer"
                className="hover:text-cyan-400 transition-colors flex items-center gap-1"
              >
                <span>PhiUSIIL Dataset</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
