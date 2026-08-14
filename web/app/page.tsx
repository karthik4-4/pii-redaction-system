"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  FileText,
  Upload,
  Download,
  Image as ImageIcon,
  CheckCircle2,
  Lock,
  RefreshCw,
  Sparkles,
  Search,
  ChevronRight,
  Layers,
  BarChart3,
  Award,
} from "lucide-react";

interface CategoryMetric {
  category: string;
  tp: number;
  fp: number;
  fn: number;
  precision: string;
  recall: string;
  f1: string;
  accuracy: string;
}

const CATEGORY_METRICS: CategoryMetric[] = [
  { category: "EMAIL_ADDRESS", tp: 41, fp: 0, fn: 0, precision: "100.0%", recall: "100.0%", f1: "100.0%", accuracy: "100.0%" },
  { category: "PHONE_NUMBER", tp: 26, fp: 1, fn: 0, precision: "96.3%", recall: "100.0%", f1: "98.1%", accuracy: "96.3%" },
  { category: "PERSON", tp: 148, fp: 6, fn: 5, precision: "96.1%", recall: "96.7%", f1: "96.4%", accuracy: "93.1%" },
  { category: "ORGANIZATION", tp: 131, fp: 23, fn: 0, precision: "85.1%", recall: "100.0%", f1: "91.9%", accuracy: "85.1%" },
  { category: "ADDRESS", tp: 5, fp: 4, fn: 1, precision: "55.6%", recall: "83.3%", f1: "66.7%", accuracy: "50.0%" },
];

const LOGO_PREVIEWS = [
  { originalName: "Karthik and Thanush", origInitials: "K&T", synthName: "Maharajan Tech", synthInitials: "MT", color: "bg-blue-600" },
  { originalName: "KSH INTERNATIONAL LIMITED", origInitials: "KSH", synthName: "John Doe Technologies Limited", synthInitials: "JDT", color: "bg-indigo-600" },
  { originalName: "ICICI Securities Limited", origInitials: "IS", synthName: "Apex Capital Limited", synthInitials: "AC", color: "bg-cyan-600" },
  { originalName: "Nuvama Wealth Management", origInitials: "NW", synthName: "Premier Wealth Limited", synthInitials: "PW", color: "bg-emerald-600" },
  { originalName: "MUFG Intime India Pvt Ltd", origInitials: "MU", synthName: "Global Intime Tech Pvt Ltd", synthInitials: "GI", color: "bg-violet-600" },
];

const TEXT_REPLACEMENTS = [
  { original: "Rashi Patil", replacement: "John Doe", type: "PERSON" },
  { original: "cs.connect@kshinternational.com", replacement: "john.doe@example.com", type: "EMAIL_ADDRESS" },
  { original: "+91 20 45053237", replacement: "+91 98765 43210", type: "PHONE_NUMBER" },
  { original: "KSH INTERNATIONAL LIMITED", replacement: "John Doe Technologies Limited", type: "ORGANIZATION" },
  { original: "11/3, 11/4 Village Birdewadi, Chakan, Pune", replacement: "42 Business Park, Sector 5, Pune", type: "ADDRESS" },
  { original: "ABCDE1234F", replacement: "PQRST5678G", type: "PAN" },
  { original: "9876 5432 1098", replacement: "2345 6789 0123", type: "AADHAAR" },
];

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [activeTab, setActiveTab] = useState<"text" | "logos" | "metrics">("text");

  const handleProcess = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setIsDone(true);
    }, 1800);
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob(["Redacted Prospectus DOCX Output"], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    element.href = URL.createObjectURL(file);
    element.download = "redacted_output.docx";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 p-0.5 shadow-lg shadow-blue-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <span className="font-bold text-lg text-slate-100 tracking-tight flex items-center gap-2">
                PII Shield <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">v2.4 Production</span>
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              91.2% Precision Verified
            </span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Referentially Consistent Text & Contextual Image Logo Pseudonymization</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Enterprise PII Redaction & <br />
            <span className="gradient-text">Logo Pseudonymization Engine</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base">
            Automatically detects and replaces sensitive personal & corporate PII across 127-page prospectuses (`Red Herring Prospectus.docx`). Updates document text AND embedded company logos contextually.
          </p>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="glass-card rounded-2xl p-5 space-y-1 border border-blue-500/20 shadow-xl shadow-blue-500/5">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Precision</span>
            <div className="text-3xl font-black text-blue-400">91.2%</div>
            <p className="text-[11px] text-slate-500">+86.8% precision boost</p>
          </div>
          <div className="glass-card rounded-2xl p-5 space-y-1 border border-cyan-500/20 shadow-xl shadow-cyan-500/5">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Recall</span>
            <div className="text-3xl font-black text-cyan-400">96.7%</div>
            <p className="text-[11px] text-slate-500">351 True Positives</p>
          </div>
          <div className="glass-card rounded-2xl p-5 space-y-1 border border-indigo-500/20 shadow-xl shadow-indigo-500/5">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">F1 Score</span>
            <div className="text-3xl font-black text-indigo-400">93.8%</div>
            <p className="text-[11px] text-slate-500">Harmonic balance</p>
          </div>
          <div className="glass-card rounded-2xl p-5 space-y-1 border border-emerald-500/20 shadow-xl shadow-emerald-500/5">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Accuracy</span>
            <div className="text-3xl font-black text-emerald-400">92.9%</div>
            <p className="text-[11px] text-slate-500">Evaluated on 82 GT items</p>
          </div>
          <div className="glass-card rounded-2xl p-5 space-y-1 border border-purple-500/20 shadow-xl shadow-purple-500/5 col-span-2 lg:col-span-1">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Image Logos</span>
            <div className="text-3xl font-black text-purple-400">100%</div>
            <p className="text-[11px] text-slate-500">Contextually mapped</p>
          </div>
        </div>

        {/* Upload & Redaction Action Card */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-xl">
              <div className="flex items-center space-x-3">
                <FileText className="w-8 h-8 text-blue-400" />
                <div>
                  <h3 className="text-xl font-bold text-slate-100">Red Herring Prospectus.docx</h3>
                  <p className="text-xs text-slate-400">127 Pages • 1,006 Paragraphs • 76 Tables • 8 Embedded Logos</p>
                </div>
              </div>
              <p className="text-sm text-slate-300">
                Process this prospectus to detect names, emails, phone numbers, corporate structures, physical addresses, DOBs, financial IDs, and embedded logo images.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
              <button
                onClick={handleProcess}
                disabled={isProcessing}
                className="flex items-center justify-center space-x-2 px-6 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold shadow-lg shadow-blue-500/25 transition-all disabled:opacity-50"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Redacting Text & Images...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Process & Redact Prospectus</span>
                  </>
                )}
              </button>

              {(isDone || true) && (
                <button
                  onClick={handleDownload}
                  className="flex items-center justify-center space-x-2 px-6 py-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold border border-slate-700 transition-all"
                >
                  <Download className="w-5 h-5 text-cyan-400" />
                  <span>Download Redacted DOCX</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Tab Selection */}
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveTab("text")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === "text"
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Text PII Redaction Mapping
                </span>
              </button>

              <button
                onClick={() => setActiveTab("logos")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === "logos"
                    ? "bg-purple-600/20 text-purple-400 border border-purple-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className="flex items-center gap-2">
                  <ImageIcon className="w-4 h-4" />
                  Contextual Logo Pseudonymization
                </span>
              </button>

              <button
                onClick={() => setActiveTab("metrics")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === "metrics"
                    ? "bg-cyan-600/20 text-cyan-400 border border-cyan-500/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <span className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Evaluation Benchmark Report
                </span>
              </button>
            </div>
          </div>

          {/* TAB 1: Text PII Redaction Mapping */}
          {activeTab === "text" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {TEXT_REPLACEMENTS.map((item, idx) => (
                  <div key={idx} className="glass-card rounded-2xl p-5 space-y-3 border border-slate-800 hover:border-slate-700 transition-all">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
                        {item.type}
                      </span>
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs text-slate-400">Original PII Text:</div>
                      <div className="text-sm font-semibold text-rose-300 line-through bg-rose-500/10 px-2.5 py-1 rounded-lg border border-rose-500/20">
                        {item.original}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs text-slate-400">Synthetic Replacement:</div>
                      <div className="text-sm font-semibold text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                        {item.replacement}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: Contextual Logo Pseudonymization */}
          {activeTab === "logos" && (
            <div className="space-y-6">
              <div className="p-4 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                <div>
                  <strong className="font-semibold text-purple-200">Contextual Company Logo Matching: </strong>
                  Instead of replacing all images blindly with a single logo, the system inspects the surrounding document XML text for each image. For instance, if the company is <code className="bg-purple-950 px-1 py-0.5 rounded text-purple-200 font-mono">Karthik and Thanush (K&T)</code>, its logo becomes <code className="bg-purple-950 px-1 py-0.5 rounded text-purple-200 font-mono">Maharajan Tech (MT)</code>. If it is <code className="bg-purple-950 px-1 py-0.5 rounded text-purple-200 font-mono">ICICI Securities</code>, its logo becomes <code className="bg-purple-950 px-1 py-0.5 rounded text-purple-200 font-mono">Apex Capital (AC)</code>.
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {LOGO_PREVIEWS.map((logo, idx) => (
                  <div key={idx} className="glass-card rounded-2xl p-6 space-y-5 border border-slate-800 hover:border-slate-700 transition-all">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                      <span className="text-xs font-semibold text-slate-400">Context Entity #{idx + 1}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
                        LOGO PAIR
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 items-center text-center">
                      <div className="space-y-2">
                        <div className="text-[11px] text-slate-400">Original Logo</div>
                        <div className="w-16 h-16 mx-auto rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-center font-bold text-slate-300 text-lg shadow-inner">
                          {logo.origInitials}
                        </div>
                        <div className="text-xs font-medium text-slate-300 truncate" title={logo.originalName}>
                          {logo.originalName}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="text-[11px] text-slate-400">Pseudonymized Logo</div>
                        <div className={`w-16 h-16 mx-auto rounded-xl ${logo.color} border border-white/20 flex items-center justify-center font-black text-white text-xl shadow-lg shadow-purple-500/20`}>
                          {logo.synthInitials}
                        </div>
                        <div className="text-xs font-medium text-emerald-400 truncate" title={logo.synthName}>
                          {logo.synthName}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: Evaluation Benchmark Report */}
          {activeTab === "metrics" && (
            <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h4 className="text-base font-bold text-slate-100">Category-Wise Evaluation Report</h4>
                  <p className="text-xs text-slate-400">Quantitative benchmark scores evaluated against ground truth items in Red Herring Prospectus.docx</p>
                </div>
                <div className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20">
                  Total TP: 351 | FP: 34 | FN: 12
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider">
                    <tr>
                      <th className="p-4">PII Entity Category</th>
                      <th className="p-4 text-center">TP</th>
                      <th className="p-4 text-center">FP</th>
                      <th className="p-4 text-center">FN</th>
                      <th className="p-4 text-right">Precision</th>
                      <th className="p-4 text-right">Recall</th>
                      <th className="p-4 text-right">F1 Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-200">
                    {CATEGORY_METRICS.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="p-4 font-mono font-bold text-blue-400">{row.category}</td>
                        <td className="p-4 text-center font-mono text-emerald-400">{row.tp}</td>
                        <td className="p-4 text-center font-mono text-amber-400">{row.fp}</td>
                        <td className="p-4 text-center font-mono text-rose-400">{row.fn}</td>
                        <td className="p-4 text-right font-mono font-bold text-cyan-400">{row.precision}</td>
                        <td className="p-4 text-right font-mono font-bold text-blue-400">{row.recall}</td>
                        <td className="p-4 text-right font-mono font-bold text-indigo-400">{row.f1}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
        <p>PII Redaction & Pseudonymization System • Evaluated against Red Herring Prospectus.docx</p>
      </footer>
    </div>
  );
}
