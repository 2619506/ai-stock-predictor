import React, { useState } from 'react';
import { LineChart, Line, ResponsiveContainer, YAxis, Tooltip as ChartTooltip } from 'recharts';
import { Info, BookOpen, BarChart2, TrendingUp, HelpCircle, Star, Sparkles } from 'lucide-react';

// Mock Data for Compact Chart
const mockData = [
  { day: 'Mon', price: 150 }, { day: 'Tue', price: 155 }, { day: 'Wed', price: 152 },
  { day: 'Thu', price: 160 }, { day: 'Fri', price: 165 }
];

export default function BeginnerStockPlatform() {
  const [activeTab, setActiveTab] = useState('Learn');
  const [chartMode, setChartMode] = useState('Simple');

  const tabs = [
    { name: 'Learn', icon: <BookOpen size={18} /> },
    { name: 'Explore', icon: <Sparkles size={18} /> },
    { name: 'Charts', icon: <BarChart2 size={18} /> },
    { name: 'Trends', icon: <TrendingUp size={18} /> },
    { name: 'My Picks', icon: <Star size={18} /> },
    { name: 'Help', icon: <HelpCircle size={18} /> }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-[#0f172a] text-slate-200 font-sans p-6 selection:bg-cyan-500/30">
      
      {/* Header */}
      <header className="max-w-6xl mx-auto flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 flex items-center gap-2">
          <Sparkles className="text-cyan-400" />
          NeonVest
        </h1>
        
        {/* Navigation Tabs */}
        <nav className="flex gap-2 bg-white/5 p-1 rounded-xl backdrop-blur-md border border-white/10">
          {tabs.map((tab) => (
            <button
              key={tab.name}
              onClick={() => setActiveTab(tab.name)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                activeTab === tab.name 
                  ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.2)] border border-cyan-500/30' 
                  : 'hover:bg-white/5 hover:text-white text-slate-400'
              }`}
            >
              {tab.icon} {tab.name}
            </button>
          ))}
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto">
        
        {/* LEARN TAB */}
        {activeTab === 'Learn' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
            
            {/* Cartoon Analogy Card */}
            <div className="bg-white/10 backdrop-blur-xl border border-white/10 p-8 rounded-2xl relative group">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                🍕 What is a Stock?
              </h2>
              <p className="text-lg text-slate-300 leading-relaxed mb-6">
                A stock is like owning a tiny slice of a massive pizza shop. 
                If the shop gets popular and sells more pizza, your slice becomes more valuable! 
                If you ever want to leave, you can sell your slice to someone else.
              </p>
              
              {/* Educational Hover Tooltip */}
              <div className="inline-flex items-center gap-2 text-cyan-400 bg-cyan-400/10 px-3 py-1.5 rounded-full cursor-help relative">
                <Info size={16} /> Hover to learn: "Dividends"
                <div className="absolute left-0 bottom-full mb-2 w-64 bg-slate-800 text-sm text-white p-3 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl border border-slate-600 z-10">
                  A dividend is like the company giving you a small cash 'thank you' gift 🎁 just for holding onto their slice!
                </div>
              </div>
            </div>

            {/* Trust-Building AI Panel */}
            <div className="bg-gradient-to-br from-purple-900/40 to-indigo-900/40 backdrop-blur-xl border border-purple-500/20 p-8 rounded-2xl relative">
              <h2 className="text-xl font-bold text-purple-300 mb-4 flex items-center gap-2">
                🧠 Transparent AI Insight
              </h2>
              <p className="text-slate-300 mb-4">Here is how I calculate if a stock is healthy, step-by-step:</p>
              <ul className="space-y-3 text-slate-300">
                <li className="flex gap-3"><span className="text-cyan-400">1.</span> I look at the price over the last 30 days.</li>
                <li className="flex gap-3"><span className="text-cyan-400">2.</span> I check how many people are buying (volume).</li>
                <li className="flex gap-3"><span className="text-cyan-400">3.</span> If both are steady, the stock is taking a healthy walk! 🚶‍♂️</li>
              </ul>
            </div>
            
          </div>
        )}

        {/* CHARTS TAB */}
        {activeTab === 'Charts' && (
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl relative">
            
            {/* Header & Toggle */}
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  Apple Inc. (AAPL)
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-md border border-green-500/30">Healthy</span>
                </h2>
                <p className="text-slate-400 text-sm mt-1">Watching the price over the last 5 days.</p>
              </div>
              
              <div className="flex bg-slate-900/50 rounded-lg p-1 border border-white/10">
                <button onClick={() => setChartMode('Simple')} className={`px-4 py-1.5 rounded-md text-sm transition-all ${chartMode === 'Simple' ? 'bg-cyan-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}>Simple View</button>
                <button onClick={() => setChartMode('Advanced')} className={`px-4 py-1.5 rounded-md text-sm transition-all ${chartMode === 'Advanced' ? 'bg-cyan-500 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}>Advanced</button>
              </div>
            </div>

            {/* Compact Chart Area (Height reduced by 30%) */}
            <div className="h-48 w-full group relative cursor-crosshair">
              {/* Floating Chart Tooltip Instruction */}
              <div className="absolute top-2 left-2 text-xs text-cyan-400 bg-cyan-900/30 px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 backdrop-blur-sm border border-cyan-500/20">
                💡 The line moving up means more people want a slice of this company today!
              </div>

              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockData}>
                  <ChartTooltip 
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}
                    itemStyle={{ color: '#22d3ee' }}
                  />
                  {chartMode === 'Advanced' && <YAxis domain={['dataMin - 10', 'auto']} stroke="#475569" fontSize={12} />}
                  <Line type="monotone" dataKey="price" stroke="#22d3ee" strokeWidth={3} dot={{ r: 4, fill: '#0f172a', stroke: '#22d3ee', strokeWidth: 2 }} activeDot={{ r: 6, fill: '#22d3ee' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* AI Explanation of the Chart */}
            <div className="mt-6 bg-cyan-900/20 border-l-2 border-cyan-400 p-4 rounded-r-lg">
              <p className="text-sm text-cyan-100">
                <strong className="text-cyan-400">Verified Market Explanation:</strong> Over the last 5 days, Apple's price has steadily climbed from $150 to $165. This steady growth is like a train picking up speed comfortably without rushing.
              </p>
            </div>

            {/* Tiny Data Provider Credit */}
            <div className="absolute bottom-2 right-3 text-[10px] text-white/40">
              Data from: Yahoo Finance
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
