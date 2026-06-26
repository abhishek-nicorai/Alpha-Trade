import { useState, useEffect, useRef } from 'react';

export const useTradingSocket = (url) => {
  // Initial state matches the structure expected by Dashboard.jsx
  const [liveData, setLiveData] = useState({ prices: {}, pnl: 0, margin: 10000 });
  const [isConnected, setIsConnected] = useState(false);
  
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    if (!url) return;

    const connect = () => {
      // Clear any existing timeout to prevent multiple connection attempts
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);

      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log("🚀 Connected to AlphaTrade Live Stream");
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          // 1. Handle SYSTEM_UPDATE (The Heartbeat from main_bot.py)
          // This contains the full dictionary of all watched stocks
          if (message.type === "SYSTEM_UPDATE") {
            setLiveData(prev => ({
              ...prev,
              prices: message.prices || prev.prices, // message.prices is {token: {symbol, ltp}}
              pnl: message.pnl ?? prev.pnl,
              margin: message.margin ?? prev.margin
            }));
          }

          // 2. Handle MARKET_UPDATE (Individual ticks from streamer.py)
          if (message.type === "MARKET_UPDATE") {
            setLiveData(prev => {
              const existingStockData = prev.prices[message.token] || {};
              return {
                ...prev,
                prices: {
                  ...prev.prices,
                  [message.token]: {
                    ...existingStockData,
                    symbol: message.symbol || existingStockData.symbol || `Token ${message.token}`,
                    ltp: message.ltp,
                    // Preserve existing qty/entry/pnl if they exist
                    qty: message.qty ?? existingStockData.qty,
                    entry: message.entry ?? existingStockData.entry,
                    pnl: message.pnl ?? existingStockData.pnl
                  }
                }
              };
            });
          }
        } catch (e) {
          console.error("Data parse error:", e);
        }
      };

      socket.onclose = (e) => {
        setIsConnected(false);
        // Only retry if the component is still mounted and it wasn't a clean close
        if (e.code !== 1000) {
          console.log("WebSocket closed. Retrying in 5s...");
          reconnectTimeoutRef.current = setTimeout(connect, 5000);
        }
      };

      socket.onerror = (err) => {
        console.error("WebSocket Error:", err);
        setIsConnected(false);
      };
    };

    connect();

    // CLEANUP logic: Closes the connection when you leave the page
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) {
        socketRef.current.close(1000, "Closing Normally");
      }
    };
  }, [url]);

  return { liveData, isConnected };
};