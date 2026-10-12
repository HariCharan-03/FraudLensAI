import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import type { ScanResult, ChatMessage } from '../types';
import { api } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import {
  Bot,
  Send,
  User,
  BookOpen,
  ExternalLink,
  Sparkles,
  Activity,
  Layers,
  ArrowRight,
} from 'lucide-react';

export const AssistantPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const scanIdParam = searchParams.get('scanId');

  const [scans, setScans] = useState<ScanResult[]>([]);
  const [selectedScanId, setSelectedScanId] = useState<string>(scanIdParam || '');
  const [activeScan, setActiveScan] = useState<ScanResult | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [asking, setAsking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load available scans for selector
  useEffect(() => {
    api.listScans(undefined, undefined, 20).then((res) => {
      setScans(res.items);
      if (!selectedScanId && res.items.length > 0) {
        setSelectedScanId(res.items[0].id);
      }
    });
  }, []);

  // When selected scan changes, load scan details and chat history
  useEffect(() => {
    if (!selectedScanId) return;
    setLoading(true);

    Promise.all([
      api.getScan(selectedScanId),
      api.getChatHistory(selectedScanId),
    ])
      .then(([scanData, chatHistory]) => {
        setActiveScan(scanData);
        setMessages(chatHistory);
      })
      .catch((err) => console.error('Error loading assistant context:', err))
      .finally(() => setLoading(false));
  }, [selectedScanId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, asking]);

  const handleSend = async (qToSend?: string) => {
    const question = qToSend || inputQuestion.trim();
    if (!question || !selectedScanId || asking) return;

    setInputQuestion('');
    setAsking(true);

    // Optimistically add user message
    const tempUserMsg: ChatMessage = {
      id: 'temp-' + Date.now(),
      scan_id: selectedScanId,
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.askAssistant(selectedScanId, question);
      const assistantMsg: ChatMessage = {
        id: 'resp-' + Date.now(),
        scan_id: selectedScanId,
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: 'err-' + Date.now(),
        scan_id: selectedScanId,
        role: 'assistant',
        content: `Assistant encountered an issue: ${err.message}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setAsking(false);
    }
  };

  const quickQuestions = [
    'Why was this URL flagged?',
    'Which features influenced the model most?',
    'What should I do if I entered credentials?',
    'How can I verify this website safely?',
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Bot className="w-6 h-6 text-cyan-400" /> Grounded AI Security Analyst
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Retrieval-Augmented Generation (RAG) assistant answering questions grounded in scan evidence and CISA/OWASP standards.
          </p>
        </div>

        {/* Scan Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">Scan Context:</span>
          <select
            value={selectedScanId}
            onChange={(e) => setSelectedScanId(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-400 max-w-xs truncate"
          >
            {scans.map((s) => (
              <option key={s.id} value={s.id}>
                [{s.risk_level}] {s.url}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!activeScan && !loading ? (
        <div className="cyber-card rounded-2xl p-12 text-center border border-slate-800 max-w-md mx-auto my-12 space-y-3">
          <Layers className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-bold text-white">No Active Scan Selected</h3>
          <p className="text-xs text-slate-500">
            Please run a scan first so the assistant has concrete security evidence to ground its responses.
          </p>
          <Link
            to="/scan"
            className="inline-block px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 font-bold text-xs"
          >
            Go to Scanner
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Active Scan Summary Sidebar (Width 4/12) */}
          <div className="lg:col-span-4 space-y-4">
            {activeScan && (
              <div className="cyber-card rounded-xl p-5 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400 font-bold uppercase tracking-wider">
                    Grounded Scan
                  </span>
                  <RiskBadge level={activeScan.risk_level} size="sm" />
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-white truncate" title={activeScan.url}>
                  {activeScan.url}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-500 text-[10px] block">RISK SCORE</span>
                    <span className="text-white font-bold text-sm">{activeScan.risk_score} / 100</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-500 text-[10px] block">MODEL P(PHISH)</span>
                    <span className="text-cyan-400 font-bold text-sm">
                      {activeScan.model_score !== null && activeScan.model_score !== undefined
                        ? `${(activeScan.model_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-500 block mb-1">DECISION SUMMARY</span>
                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-2.5 rounded border border-slate-800/80">
                    {activeScan.plain_explanation || 'Comprehensive assessment compiled from URL and security intelligence.'}
                  </p>
                </div>

                <Link
                  to={`/scan/${activeScan.id}`}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 pt-1"
                >
                  <span>View Full Forensic Report</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}

            {/* Quick Suggested Prompts */}
            <div className="cyber-card rounded-xl p-5 border border-slate-800 space-y-2.5">
              <span className="text-xs font-mono text-slate-400 font-bold uppercase tracking-wider block">
                Suggested Security Prompts
              </span>
              <div className="space-y-1.5">
                {quickQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(q)}
                    disabled={asking}
                    className="w-full text-left p-2.5 rounded-lg bg-slate-900 hover:bg-slate-800/80 border border-slate-800 text-xs text-slate-300 hover:text-cyan-300 transition-colors cursor-pointer flex items-center justify-between group disabled:opacity-50"
                  >
                    <span>{q}</span>
                    <Sparkles className="w-3 h-3 text-cyan-500 opacity-60 group-hover:opacity-100" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Interactive Chat Window (Width 8/12) */}
          <div className="lg:col-span-8 flex flex-col cyber-card rounded-xl border border-slate-800 h-[680px]">
            {/* Chat Messages Log */}
            <div className="flex-1 p-5 overflow-y-auto space-y-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center p-8 space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
                    <Bot className="w-6 h-6" />
                  </div>
                  <h4 className="text-sm font-bold text-white">Ask Anything About This Forensic Scan</h4>
                  <p className="text-xs text-slate-400 max-w-sm">
                    Inquire why specific features were flagged, request incident response guidance, or ask how to verify safe identity.
                  </p>
                </div>
              ) : (
                messages.map((msg) => {
                  const isUser = msg.role === 'user';
                  return (
                    <div key={msg.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
                      {!isUser && (
                        <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800/40 flex items-center justify-center text-cyan-400 shrink-0">
                          <Bot className="w-4 h-4" />
                        </div>
                      )}

                      <div
                        className={`max-w-2xl rounded-xl p-4 text-xs leading-relaxed space-y-3 ${
                          isUser
                            ? 'bg-cyan-600 text-slate-950 font-medium'
                            : 'bg-slate-900 border border-slate-800 text-slate-200'
                        }`}
                      >
                        <div className="whitespace-pre-wrap">{msg.content}</div>

                        {/* RAG Document Citations */}
                        {msg.citations && msg.citations.length > 0 && (
                          <div className="pt-3 border-t border-slate-800/80 space-y-1.5">
                            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block flex items-center gap-1">
                              <BookOpen className="w-3 h-3 text-cyan-400" /> Retrieved Security Citations:
                            </span>
                            <div className="space-y-1">
                              {msg.citations.map((c, idx) => (
                                <a
                                  key={idx}
                                  href={c.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 border border-slate-800/60 text-[11px] text-cyan-400 hover:text-cyan-300 font-mono transition-colors"
                                >
                                  <span className="truncate">{c.citation} ({c.organization})</span>
                                  <ExternalLink className="w-3 h-3 shrink-0 ml-1.5 text-slate-500" />
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {isUser && (
                        <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                          <User className="w-4 h-4" />
                        </div>
                      )}
                    </div>
                  );
                })
              )}

              {asking && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800/40 flex items-center justify-center text-cyan-400 shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-400 flex items-center gap-2 font-mono">
                    <Activity className="w-4 h-4 animate-spin text-cyan-400" />
                    <span>Retrieving cybersecurity knowledge & synthesizing evidence...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input Box */}
            <div className="p-4 border-t border-slate-800 bg-slate-950/40">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  value={inputQuestion}
                  onChange={(e) => setInputQuestion(e.target.value)}
                  placeholder="Ask a question about this scan or incident remediation..."
                  disabled={asking || !selectedScanId}
                  className="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs font-mono focus:outline-none focus:border-cyan-400 disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={asking || !inputQuestion.trim() || !selectedScanId}
                  className="px-4 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md disabled:opacity-50 transition-all cursor-pointer"
                >
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
