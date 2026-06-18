import React, { useState } from 'react';
import { Save, ShieldCheck, TrendingUp, AlertTriangle } from 'lucide-react';
import { botService } from '../services/api';
import axios from 'axios';

const Settings = () => {
  const [capital, setCapital] = useState(10000);
  const [maxTrades, setMaxTrades] = useState(3);
  const [isSaving, setIsSaving] = useState(false);
  const [mode, setMode] = useState("PAPER");

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await botService.updateSettings({ capital, max_trades: maxTrades });
      alert("✅ Settings Synced to Bot Engine!");
    } catch (err) {
      alert("❌ Failed to update settings.");
    }
    setIsSaving(false);
  };

  const handleModeChange = async (newMode) => {
    if (newMode === "LIVE") {
      const confirmed = window.confirm(
        "🚨 WARNING: You are activating REAL MONEY trading. Are you sure?"
      );

      if (!confirmed) return;
    }

    try {
      await botService.changeMode(newMode);

      setMode(newMode);

      alert(`System set to ${newMode} mode.`);
    } catch (err) {
      alert("Failed to switch mode");
    }
  };

  return (
    <div className="p-10 max-w-4xl animate-in slide-in-from-right-4 duration-500">
      <h1 className="text-3xl font-bold mb-2">Bot <span className="text-blue-500">Settings</span></h1>
      <p className="text-text-secondary mb-10 text-sm">Configure your risk parameters and capital allocation.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* RISK CARD */}
        <div className="bg-bg-secondary p-8 rounded-2xl border border-border-muted shadow-xl space-y-6">
          <div className="flex items-center gap-3 text-blue-400 font-bold mb-4">
            <ShieldCheck size={20} /> RISK CONTROLS
          </div>

          <div>
            <label className="block text-[10px] font-black text-text-secondary uppercase mb-2">Capital Allocation (₹)</label>
            <input
              type="number"
              className="w-full bg-bg-primary border border-border-muted p-4 rounded-xl text-xl font-mono focus:border-blue-500 outline-none transition-all"
              value={capital}
              onChange={(e) => setCapital(e.target.value)}
            />
            <p className="text-[10px] text-text-secondary mt-2 italic">* Max available capital: ₹10,000</p>
          </div>

          <div>
            <label className="block text-[10px] font-black text-text-secondary uppercase mb-2">Max Daily Trades</label>
            <select
              className="w-full bg-bg-primary border border-border-muted p-4 rounded-xl text-sm focus:border-blue-500 outline-none"
              value={maxTrades}
              onChange={(e) => setMaxTrades(e.target.value)}
            >
              <option value="1">1 Trade (Conservative)</option>
              <option value="3">3 Trades (Standard)</option>
              <option value="5">5 Trades (Aggressive)</option>
            </select>
          </div>
        </div>

        {/* INFO CARD */}
        <div className="space-y-6">
          <div className="bg-blue-600/10 border border-blue-600/20 p-6 rounded-2xl">
            <div className="flex items-center gap-2 text-blue-400 font-bold mb-2">
              <TrendingUp size={18} /> 5x Leverage Active
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">
              With ₹{capital} capital, your actual buying power is <span className="text-white font-bold">₹{capital * 5}</span>.
              The bot will automatically manage position sizing based on this limit.
            </p>
          </div>

          <div className="bg-warning/10 border border-warning/20 p-6 rounded-2xl">
            <div className="flex items-center gap-2 text-warning font-bold mb-2">
              <AlertTriangle size={18} /> Safety Guard
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">
              The bot will automatically trigger a <span className="text-white font-bold text-loss">Hard Stop</span> if your daily loss exceeds 2% of allocated capital.
            </p>
          </div>
        </div>
      </div>
      <div className="bg-bg-secondary p-6 rounded-2xl border border-border-muted mt-6">
        <h3 className="text-xs font-black text-text-secondary uppercase mb-4">
          Execution Mode
        </h3>

        <div className="flex bg-bg-primary p-1 rounded-xl gap-1">

          <button
            onClick={() => handleModeChange("PAPER")}
            className={`flex-1 py-3 rounded-lg font-bold text-sm transition-all ${mode === "PAPER"
                ? "bg-blue-600 text-white"
                : "text-text-secondary"
              }`}
          >
            VIRTUAL (PAPER)
          </button>

          <button
            onClick={() => handleModeChange("LIVE")}
            className={`flex-1 py-3 rounded-lg font-bold text-sm transition-all ${mode === "LIVE"
                ? "bg-loss text-white animate-pulse"
                : "text-text-secondary"
              }`}
          >
            REAL MONEY (LIVE)
          </button>

        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={isSaving}
        className="mt-10 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-black py-4 px-10 rounded-xl flex items-center gap-3 transition-all shadow-lg shadow-blue-900/30"
      >
        <Save size={18} /> {isSaving ? "SYNCING..." : "SAVE & SYNC SETTINGS"}
      </button>
    </div>
  );
};

export default Settings;