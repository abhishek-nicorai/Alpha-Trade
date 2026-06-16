import axios from 'axios';

// Note: We added /api/v1 because of our backend refactor
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});

export const botService = {
  getStatus: () => apiClient.get('/status'),
  triggerKill: () => apiClient.post('/risk/kill'),
  updateSettings: (settings) => apiClient.post('/settings/update', settings),

  getMarketMovers: (period) => apiClient.get(`/market/movers/${period}`),
  
  // Placeholder for when we add search later
  addToWatchlist: (symbol) => apiClient.post('/market/watchlist/add', { symbol }),

  searchStocks: (query) => apiClient.get(`/market/search?q=${query}`),
  addToWatchlist: (stock) => apiClient.post('/market/watchlist/add', stock),
};