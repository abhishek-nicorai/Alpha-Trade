import React from 'react';
import { useTradingSocket } from '../hooks/useTradingSocket';
import MetricCard from '../components/MetricCard';
import { ShieldAlert, List, Zap, Activity } from 'lucide-react';
import { botService } from '../services/api';

const Dashboard = () => {
  // 1. Connect to the Real-time Nervous System
  const { liveData, isConnected } = useTradingSocket("ws://localhost:8000/api/v1/ws/live");

  const handleKillSwitch = async () => {
    if (window.confirm("EMERGENCY: Are you sure you want to exit all positions?")) {
      await botService.triggerKill();
      alert("Kill Switch Activated: System Halted.");
    }
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-500">
      {/* HEADER SECTION */}
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-sm font-black text-text-secondary uppercase tracking-[0.2em] mb-1">Command Center</h2>
          <h1 className="text-3xl font-bold">Live <span className="text-blue-500">Portfolio</span></h1>
        </div>
        <button 
          onClick={handleKillSwitch}
          className="bg-loss hover:bg-red-700 text-white px-6 py-3 rounded-lg font-black text-xs flex items-center gap-2 transition-all shadow-lg shadow-red-900/20"
        >
          <ShieldAlert size={18} /> EMERGENCY SQUARE-OFF
        </button>
      </div>

      {/* METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard 
          label="Live MTM / P&L" 
          value={`₹ ${liveData.pnl.toFixed(2)}`} 
          color={liveData.pnl >= 0 ? "text-profit" : "text-loss"} 
        />
        <MetricCard label="Margin Utilized" value={`₹ ${liveData.margin}`} />
        <MetricCard label="Active Trades" value={`${Object.keys(liveData.prices).length} / 3`} />
        <MetricCard 
          label="System Status" 
          value={isConnected ? "OPERATIONAL" : "OFFLINE"} 
          color={isConnected ? "text-profit" : "text-loss"} 
        />
      </div>

      {/* POSITIONS TABLE */}
      <div className="bg-bg-secondary rounded-xl border border-border-muted overflow-hidden shadow-2xl">
        <div className="px-6 py-4 bg-bg-tertiary border-b border-border-muted flex justify-between items-center">
          <h3 className="font-bold text-sm flex items-center gap-2">
            <List size={16} className="text-blue-400" /> Active Positions
          </h3>
          <span className="text-[10px] text-text-secondary font-mono">Real-time Sync Active</span>
        </div>
        
        <table className="w-full text-left">
          <thead className="text-[10px] uppercase text-text-secondary bg-bg-primary/50">
            <tr>
              <th className="px-6 py-4">Instrument</th>
              <th className="px-6 py-4">Quantity</th>
              <th className="px-6 py-4">Avg. Price</th>
              <th className="px-6 py-4">LTP (Live)</th>
              <th className="px-6 py-4 text-right">PnL</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-border-muted">
            {Object.keys(liveData.prices).length > 0 ? (
              Object.keys(liveData.prices).map((token) => (
                <tr key={token} className="hover:bg-bg-tertiary/50 transition-colors">
                  <td className="px-6 py-4 font-bold text-blue-400">TOKEN: {token}</td>
                  <td className="px-6 py-4">--</td>
                  <td className="px-6 py-4 text-text-secondary">₹ 0.00</td>
                  <td className="px-6 py-4 font-mono">₹ {liveData.prices[token]}</td>
                  <td className="px-6 py-4 text-right font-bold text-profit">+ ₹ 0.00</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="px-6 py-20 text-center text-text-secondary italic">
                  <div className="flex flex-col items-center gap-2">
                    <Activity size={32} className="opacity-20 animate-pulse" />
                    No active trades detected.
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;