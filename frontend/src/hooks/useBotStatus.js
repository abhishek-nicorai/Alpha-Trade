import { useState, useEffect } from 'react';
import { botService } from '../services/api';

export const useBotStatus = () => {
  const [status, setStatus] = useState("Checking...");

  const fetchStatus = async () => {
    try {
      const res = await botService.getStatus();
      setStatus(res.data.status);
    } catch (err) {
      setStatus("Offline");
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return status;
};