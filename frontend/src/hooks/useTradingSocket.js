import { useState, useEffect, useRef } from 'react';

export const useTradingSocket = (url) => {
  const [liveData, setLiveData] = useState({ prices: {}, pnl: 0, margin: 0 });
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!url) return;

    const connect = () => {
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log("🚀 Connected to AlphaTrade Live Stream");
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === "MARKET_UPDATE" || message.type === "SYSTEM_UPDATE") {
            setLiveData(prev => ({
              ...prev,
              prices: { ...prev.prices, [message.token]: message.ltp },
              pnl: message.pnl ?? prev.pnl,
              margin: message.margin ?? prev.margin
            }));
          }
        } catch (e) {
          console.error("Data parse error", e);
        }
      };

      socket.onclose = (e) => {
        setIsConnected(false);
        // Only try to reconnect if it wasn't a deliberate close
        if (e.code !== 1000) {
          console.log("WebSocket closed. Retrying in 3s...");
          setTimeout(connect, 3000);
        }
      };

      socket.onerror = () => {
        setIsConnected(false);
      };
    };

    connect();

    // CLEANUP logic: This stops the error you are seeing
    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, "Component Unmounted");
      }
    };
  }, [url]);

  return { liveData, isConnected };
};