import React from 'react';
import { useTradingSocket } from '../hooks/useTradingSocket';
import MetricCard from '../components/MetricCard';
import { ShieldAlert, List, Activity, Layout } from 'lucide-react';
import { botService } from '../services/api';
import WatchlistManager from '../features/WatchlistManager';

const Dashboard = () => {
  // 1. Connect to the Real-time Nervous System (Using 127.0.0.1 for Windows stability)
  const { liveData, isConnected } = useTradingSocket("ws://127.0.0.1:8000/api/v1/ws/live");

  const handleKillSwitch = async () => {
    if (window.confirm("🚨 EMERGENCY: Are you sure you want to exit all positions and halt the bot?")) {
      await botService.triggerKill();
      alert("Kill Switch Activated: System Halted.");
    }
  };

  return (
    <div className="p-8 space-y-10 animate-in fade-in duration-500 max-w-[1600px] mx-auto">
      
      {/* HEADER SECTION */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-[10px] font-black text-blue-500 uppercase tracking-[0.3em] mb-1 flex items-center gap-2">
            <Layout size={12} /> System Terminal v1.0
          </h2>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Trading <span className="text-text-secondary font-light">Cockpit</span>
          </h1>
        </div>
        <button 
          onClick={handleKillSwitch}
          className="bg-loss hover:bg-red-700 text-white px-8 py-3 rounded-xl font-black text-xs flex items-center gap-3 transition-all shadow-lg shadow-red-900/20 active:scale-95"
        >
          <ShieldAlert size={18} /> EMERGENCY SQUARE-OFF
        </button>
      </div>

      {/* NEW COMPONENT: WATCHLIST MANAGER */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 px-2">
            <Activity size={16} className="text-blue-500" />
            <span className="text-xs font-bold text-text-secondary uppercase tracking-widest">Market Targeting</span>
        </div>
        <WatchlistManager />
      </section>

      {/* METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard 
          label="Live MTM / P&L" 
          value={`₹ ${liveData.pnl.toFixed(2)}`} 
          color={liveData.pnl >= 0 ? "text-profit" : "text-loss"} 
        />
        <MetricCard label="Available Capital" value={`₹ ${liveData.margin}`} />
        <MetricCard label="Focus Stocks" value={`${Object.keys(liveData.prices).length} / 5`} />
        <MetricCard 
          label="Engine Status" 
          value={isConnected ? "OPERATIONAL" : "DISCONNECTED"} 
          color={isConnected ? "text-profit" : "text-loss"} 
        />
      </div>

      {/* POSITIONS & LIVE FEED TABLE */}
      <div className="bg-bg-secondary rounded-2xl border border-border-muted overflow-hidden shadow-2xl">
        <div className="px-6 py-4 bg-bg-tertiary border-b border-border-muted flex justify-between items-center">
          <h3 className="font-bold text-sm flex items-center gap-2">
            <List size={16} className="text-blue-400" /> Active Watchlist & Positions
          </h3>
          <div className="flex items-center gap-4">
              <span className="text-[10px] text-text-secondary font-mono flex items-center gap-1">
                <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? 'bg-profit animate-pulse' : 'bg-loss'}`}></span>
                {isConnected ? 'LIVE FEED ACTIVE' : 'FEED OFFLINE'}
              </span>
          </div>
        </div>
        
        <table className="w-full text-left border-collapse">
          <thead className="text-[10px] uppercase font-black text-text-secondary bg-bg-primary/30 tracking-widest">
            <tr>
              <th className="px-6 py-5 border-b border-border-muted">Instrument</th>
              <th className="px-6 py-5 border-b border-border-muted">Quantity</th>
              <th className="px-6 py-5 border-b border-border-muted">Entry Price</th>
              <th className="px-6 py-5 border-b border-border-muted text-blue-400">LTP (Real-time)</th>
              <th className="px-6 py-5 border-b border-border-muted text-right">Day PnL</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-border-muted">
            {Object.keys(liveData.prices).length > 0 ? (
              Object.keys(liveData.prices).map((token) => {
                const stock = liveData.prices[token];
                return (
                    <tr key={token} className="hover:bg-bg-tertiary/40 transition-colors group">
                      <td className="px-6 py-4 font-bold text-white group-hover:text-blue-400 transition-colors">
                        {stock.symbol}
                      </td>
                      <td className="px-6 py-4 font-mono text-text-secondary">
                        {stock.qty || '--'}
                      </td>
                      <td className="px-6 py-4 font-mono text-text-secondary italic">
                        ₹ {stock.entry ? stock.entry.toFixed(2) : '0.00'}
                      </td>
                      <td className="px-6 py-4 font-mono font-bold text-blue-400">
                        ₹ {stock.ltp.toFixed(2)}
                      </td>
                      <td className={`px-6 py-4 text-right font-mono font-bold ${stock.pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
                        {stock.pnl ? (stock.pnl >= 0 ? `+₹ ${stock.pnl}` : `-₹ ${Math.abs(stock.pnl)}`) : '₹ 0.00'}
                      </td>
                    </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="5" className="px-6 py-24 text-center text-text-secondary">
                  <div className="flex flex-col items-center gap-4 opacity-40">
                    <Activity size={48} className="animate-pulse" />
                    <p className="text-xs uppercase font-black tracking-widest italic">
                        Waiting for stock deployment...
                    </p>
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