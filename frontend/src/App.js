import React from 'react';
import LogInteraction from './components/LogInteraction';
import './App.css';

function App() {
  return (
    <div className="App min-h-screen" style={{
      background: 'linear-gradient(135deg, #090d16 0%, #0f172a 40%, #0f3d66 100%)'
    }}>
      {/* Top Navigation Bar */}
      <nav className="glass border-b border-white/10 px-6 py-3 flex items-center justify-between sticky top-0 z-50"
        style={{ borderRadius: 0, background: 'rgba(9,13,22,0.85)', backdropFilter: 'blur(24px)' }}>
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #0284c7, #0ea5e9)' }}>
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <span className="text-white font-bold text-sm tracking-tight">PharmaConnect</span>
            <span className="text-white/40 text-xs ml-2">HCP CRM</span>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <span className="pill">AI-Powered</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
            <span className="text-white/60 text-xs">LangGraph Active</span>
          </div>
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
            style={{ background: 'linear-gradient(135deg, #0284c7, #0ea5e9)' }}>
            TR
          </div>
        </div>
      </nav>

      <LogInteraction />
    </div>
  );
}

export default App;
