import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import MarketExplorer from './pages/MarketExplorer';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-bg-primary text-text-primary overflow-hidden">
        {/* Modular Sidebar */}
        <Sidebar />
        
        {/* Modular Page Views */}
        <main className="flex-1 overflow-y-auto custom-scrollbar">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/market" element={<MarketExplorer />} />
            <Route path="/settings" element={<Settings />} /> 
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;