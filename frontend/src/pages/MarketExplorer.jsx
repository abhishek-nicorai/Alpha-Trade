import React, { useState, useEffect, useRef } from 'react';
import { botService } from '../services/api';
import { Search, TrendingUp, TrendingDown, Calendar, Plus, Loader2 } from 'lucide-react';

const MarketExplorer = () => {
  const [period, setPeriod] = useState("TODAY");
  const [movers, setMovers] = useState({ gainers: [], losers: [] });
  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchRef = useRef(null);

  // 1. Handle Real-time Search
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (search.length >= 2) {
        setIsSearching(true);
        try {
          const res = await botService.searchStocks(search);
          setSearchResults(res.data);
        } catch (err) {
          console.error("Search error", err);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSearchResults([]);
      }
    }, 300); // Wait 300ms after user stops typing to save API calls

    return () => clearTimeout(delayDebounceFn);
  }, [search]);

  // 2. Fetch Market Movers (Gainers/Losers)
  const fetchMovers = async () => {
    try {
      const res = await botService.getMarketMovers(period);
      setMovers(res.data);
    } catch (err) {
      console.error("Fetch movers error", err);
    }
  };

  useEffect(() => {
    fetchMovers();
  }, [period]);

  // 3. Add Stock to Bot (Sends Symbol AND Token)
  const handleAddStock = async (stock) => {
    try {
      // stock object contains { symbol, token, name }
      await botService.addToWatchlist({
        symbol: stock.symbol,
        token: stock.token
      });
      alert(`🚀 ${stock.symbol} added! The bot is now watching it for ORB signals.`);
      setSearch(""); // Clear search after adding
      setSearchResults([]);
    } catch (err) {
      alert("Failed to add stock.");
    }
  };

  // Close search dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setSearchResults([]);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="p-8 space-y-8 animate-in slide-in-from-bottom-4 duration-500">
      
      {/* HEADER & SMART SEARCH */}
      <div className="flex justify-between items-center relative">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Search className="text-blue-500" /> Market <span className="text-text-secondary font-light">Explorer</span>
        </h1>
        
        <div className="relative w-96" ref={searchRef}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" size={16} />
          <input
            type="text"
            placeholder="Search all 5000+ stocks (e.g. RELIANCE)..."
            className="w-full bg-bg-secondary border border-border-muted p-3 pl-10 rounded-lg text-sm focus:border-blue-600 outline-none transition-all shadow-xl"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          
          {/* SEARCH RESULTS DROPDOWN */}
          {(searchResults.length > 0 || isSearching) && (
            <div className="absolute z-50 w-full bg-bg-secondary border border-border-muted mt-2 rounded-xl shadow-2xl overflow-hidden max-h-80 overflow-y-auto">
              {isSearching ? (
                <div className="p-4 flex justify-center"><Loader2 className="animate-spin text-blue-500" /></div>
              ) : (
                searchResults.map(stock => (
                  <div 
                    key={stock.token}
                    onClick={() => handleAddStock(stock)}
                    className="p-4 hover:bg-bg-tertiary cursor-pointer border-b border-border-muted flex justify-between items-center group transition-colors"
                  >
                    <div>
                      <div className="font-bold group-hover:text-blue-400">{stock.symbol}</div>
                      <div className="text-[10px] text-text-secondary uppercase">{stock.name}</div>
                    </div>
                    <Plus size={16} className="text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* PERIOD FILTERS */}
      <div className="flex items-center gap-4 bg-bg-secondary p-2 rounded-xl border border-border-muted w-fit shadow-lg">
        {["TODAY", "1W", "1M"].map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-6 py-2 text-xs font-black rounded-lg transition-all flex items-center gap-2 ${
              period === p ? 'bg-blue-600 text-white shadow-md' : 'text-text-secondary hover:text-white'
            }`}
          >
            <Calendar size={14} /> {p}
          </button>
        ))}
      </div>

      {/* MOVERS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* TOP GAINERS */}
        <div className="bg-bg-secondary rounded-2xl border border-border-muted overflow-hidden shadow-2xl">
          <div className="p-5 bg-profit/10 border-b border-profit/20 text-profit font-black text-xs uppercase flex justify-between items-center">
            <span className="tracking-widest">NSE Top Gainers</span>
            <TrendingUp size={18} />
          </div>
          <div className="p-3 space-y-1">
            {movers.gainers.length > 0 ? movers.gainers.map(stock => (
              <div key={stock.token} className="flex justify-between items-center p-4 hover:bg-bg-tertiary rounded-xl transition-all group">
                <span className="font-bold group-hover:text-blue-400">{stock.symbol}</span>
                <div className="flex items-center gap-4">
                  <span className="font-mono font-bold text-profit">+{stock.change}%</span>
                  <button
                    onClick={() => handleAddStock(stock)}
                    className="p-2 bg-profit/10 text-profit rounded-lg hover:bg-profit hover:text-white transition-all shadow-sm"
                  >
                    <Plus size={16} />
                  </button>
                </div>
              </div>
            )) : <p className="p-10 text-center text-text-secondary text-sm italic">Scanning for gainers...</p>}
          </div>
        </div>

        {/* TOP LOSERS */}
        <div className="bg-bg-secondary rounded-2xl border border-border-muted overflow-hidden shadow-2xl">
          <div className="p-5 bg-loss/10 border-b border-loss/20 text-loss font-black text-xs uppercase flex justify-between items-center">
            <span className="tracking-widest">NSE Top Losers</span>
            <TrendingDown size={18} />
          </div>
          <div className="p-3 space-y-1">
            {movers.losers.length > 0 ? movers.losers.map(stock => (
              <div key={stock.token} className="flex justify-between items-center p-4 hover:bg-bg-tertiary rounded-xl transition-all group">
                <span className="font-bold group-hover:text-blue-400">{stock.symbol}</span>
                <div className="flex items-center gap-4">
                  <span className="font-mono font-bold text-loss">{stock.change}%</span>
                  <button
                    onClick={() => handleAddStock(stock)}
                    className="p-2 bg-loss/10 text-loss rounded-lg hover:bg-loss hover:text-white transition-all shadow-sm"
                  >
                    <Plus size={16} />
                  </button>
                </div>
              </div>
            )) : <p className="p-10 text-center text-text-secondary text-sm italic">Scanning for losers...</p>}
          </div>
        </div>

      </div>
    </div>
  );
};

export default MarketExplorer;