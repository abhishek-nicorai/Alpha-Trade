import React, { useState, useEffect } from 'react';
import { botService } from '../services/api';
import { History, Download, Filter, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const TradeLogs = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await botService.getTradeHistory();
        setTrades(res.data.trades);
      } catch (err) {
        console.error("Failed to load history");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-700">
      {/* HEADER */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <History className="text-blue-500" /> Trade <span className="text-text-secondary font-light">Logs</span>
          </h1>
          <p className="text-xs text-text-secondary mt-1 uppercase tracking-widest">Audit Trail & Performance History</p>
        </div>
        <button className="bg-bg-secondary border border-border-muted p-2 px-4 rounded-lg text-xs font-bold flex items-center gap-2 hover:bg-bg-tertiary transition-all">
          <Download size={14} /> EXPORT CSV
        </button>
      </div>

      {/* TRADE TABLE */}
      <div className="bg-bg-secondary rounded-2xl border border-border-muted overflow-hidden shadow-2xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-bg-tertiary/50 text-[10px] uppercase font-black text-text-secondary tracking-widest">
              <th className="px-6 py-4">Timestamp</th>
              <th className="px-6 py-4">Instrument</th>
              <th className="px-6 py-4">Side</th>
              <th className="px-6 py-4">Quantity</th>
              <th className="px-6 py-4">Execution Price</th>
              <th className="px-6 py-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-border-muted">
            {loading ? (
              <tr><td colSpan="6" className="p-20 text-center animate-pulse text-text-secondary italic">Loading audit logs...</td></tr>
            ) : trades.length > 0 ? (
              trades.map((trade) => (
                <tr key={trade.id} className="hover:bg-bg-tertiary/30 transition-colors group">
                  <td className="px-6 py-4 font-mono text-[11px] text-text-secondary">
                    {new datetime(trade.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 font-bold text-blue-400">{trade.symbol}</td>
                  <td className="px-6 py-4">
                    <span className={`flex items-center gap-1 font-black text-[10px] px-2 py-1 rounded w-fit ${trade.side === 'BUY' ? 'bg-profit/10 text-profit' : 'bg-loss/10 text-loss'}`}>
                      {trade.side === 'BUY' ? <ArrowUpRight size={12}/> : <ArrowDownRight size={12}/>}
                      {trade.side}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono">{trade.qty}</td>
                  <td className="px-6 py-4 font-mono text-white">₹ {trade.entry_price.toFixed(2)}</td>
                  <td className="px-6 py-4 text-right">
                    <span className="text-[10px] bg-bg-primary px-2 py-1 rounded text-text-secondary border border-border-muted">EXECUTED</span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="p-20 text-center text-text-secondary italic">
                  No trades found in database for this period.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TradeLogs;