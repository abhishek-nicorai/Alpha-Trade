import React, { useState } from 'react';

const MarketExplorer = () => {
  const [filter, setFilter] = useState("TODAY"); // TODAY, 1W, 1M

  return (
    <div className="bg-bg-secondary p-6 rounded-lg border border-border-muted">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-bold text-lg text-blue-400 font-mono">MARKET EXPLORER</h3>
        
        {/* TIME FILTERS */}
        <div className="flex bg-bg-primary p-1 rounded-md border border-border-muted">
          {["TODAY", "1W", "1M"].map(period => (
            <button 
              key={period}
              onClick={() => setFilter(period)}
              className={`px-4 py-1 text-[10px] font-bold rounded ${filter === period ? 'bg-blue-600 text-white' : 'text-text-secondary'}`}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* TOP GAINERS */}
        <div>
          <p className="text-profit text-[10px] font-bold mb-3 uppercase tracking-widest">Top Gainers</p>
          <div className="space-y-2">
            <StockRow symbol="ZOMATO" change="+5.23%" />
            <StockRow symbol="TATAMOTORS" change="+3.81%" />
          </div>
        </div>

        {/* TOP LOSERS */}
        <div>
          <p className="text-loss text-[10px] font-bold mb-3 uppercase tracking-widest">Top Losers</p>
          <div className="space-y-2">
            <StockRow symbol="SBIN" change="-2.11%" color="text-loss" />
            <StockRow symbol="PNB" change="-1.95%" color="text-loss" />
          </div>
        </div>
      </div>
    </div>
  );
};

const StockRow = ({ symbol, change, color="text-profit" }) => (
  <div className="flex justify-between bg-bg-tertiary p-3 rounded border border-transparent hover:border-gray-600 transition-all cursor-pointer">
    <span className="font-bold text-sm">{symbol}</span>
    <span className={`font-mono text-sm ${color}`}>{change}</span>
  </div>
);

export default MarketExplorer;