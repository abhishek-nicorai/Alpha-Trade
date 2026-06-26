import React, { useState, useEffect } from 'react';
import { Search, Plus, Trash2, Send, Info, Loader2 } from 'lucide-react';
import { botService } from '../services/api';

const WatchlistManager = () => {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);

  // 1. Search Logic (Debounced)
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (search.length > 2) {
        const res = await botService.searchStocks(search);
        setResults(res.data);
      } else {
        setResults([]);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // 2. Add to Local List (Max 5)
  const addToLocal = (stock) => {
    if (watchlist.length >= 5) {
      alert("Capital Limit: You can only select 5 stocks for today.");
      return;
    }
    if (watchlist.find(s => s.token === stock.token)) return;
    setWatchlist([...watchlist, stock]);
    setSearch("");
    setResults([]);
  };

  // 3. Remove from Local List
  const removeFromLocal = (token) => {
    setWatchlist(watchlist.filter(s => s.token !== token));
  };

  // 4. Sync with Backend Bot
  const syncWithBot = async () => {
    setLoading(true);
    try {
      // Create a batch sync endpoint or call add for each
      await botService.syncWatchlist(watchlist);
      alert("🚀 Watchlist Synced! Bot is now calculating ORB for these 5 stocks.");
    } catch (err) {
      alert("Failed to sync.");
    }
    setLoading(false);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-500">
      
      {/* PANEL 1: SEARCH & DISCOVERY */}
      <div className="bg-bg-secondary p-6 rounded-2xl border border-border-muted shadow-xl">
        <h3 className="text-sm font-black text-blue-400 mb-4 uppercase tracking-widest flex items-center gap-2">
          <Search size={16} /> Find Instruments
        </h3>
        <div className="relative mb-4">
          <input 
            type="text" 
            placeholder="Search NSE Stocks..." 
            className="w-full bg-bg-primary border border-border-muted p-4 rounded-xl text-sm focus:border-blue-500 outline-none transition-all"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
          {results.map(stock => (
            <div key={stock.token} className="flex justify-between items-center bg-bg-tertiary p-3 rounded-lg group hover:border-blue-500/50 border border-transparent transition-all">
              <div>
                <div className="font-bold text-sm">{stock.symbol}</div>
                <div className="text-[10px] text-text-secondary">{stock.name}</div>
              </div>
              <button 
                onClick={() => addToLocal(stock)}
                className="p-2 bg-blue-600/10 text-blue-500 rounded-md hover:bg-blue-600 hover:text-white transition-all"
              >
                <Plus size={16} />
              </button>
            </div>
          ))}
          {search.length > 0 && results.length === 0 && (
            <p className="text-center py-10 text-text-secondary text-xs italic">No stocks found...</p>
          )}
        </div>
      </div>

      {/* PANEL 2: TODAY'S FOCUS LIST */}
      <div className="bg-bg-secondary p-6 rounded-2xl border border-border-muted shadow-xl flex flex-col">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-sm font-black text-profit mb-0 uppercase tracking-widest">
            Today's Selection ({watchlist.length}/5)
          </h3>
          {watchlist.length > 0 && (
             <button 
                onClick={syncWithBot}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 shadow-lg shadow-blue-900/40"
             >
               {loading ? <Loader2 className="animate-spin" size={14}/> : <Send size={14} />} 
               DEPLOY TO BOT
             </button>
          )}
        </div>

        <div className="flex-1 space-y-3">
          {watchlist.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-text-secondary border-2 border-dashed border-border-muted rounded-xl p-10">
               <p className="text-xs text-center italic leading-relaxed">
                 Select up to 5 stocks from the left panel to begin your automated session.
               </p>
            </div>
          ) : (
            watchlist.map(stock => (
              <div key={stock.token} className="flex justify-between items-center bg-bg-primary p-4 rounded-xl border border-border-muted group">
                <span className="font-mono font-bold text-blue-400">{stock.symbol}</span>
                <button 
                  onClick={() => removeFromLocal(stock.token)}
                  className="text-text-secondary hover:text-loss transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
};

export default WatchlistManager;