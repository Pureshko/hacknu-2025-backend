import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const accommodationService = {
  getAll: (params = {}) => 
    api.get('/api/accommodations', { params }),
  
  getById: (id) => 
    api.get(`/api/accommodations/${id}`),
  
  startScan: (region) => 
    api.post('/api/scan/start', null, { params: { region } }),
  
  generateOutreach: (id, channel = 'whatsapp') => 
    api.post(`/api/accommodations/${id}/outreach`, null, { 
      params: { channel } 
    }),
  
  exportCSV: () => 
    api.get('/api/export/csv', { responseType: 'blob' }),
};

export const analyticsService = {
  getDashboard: () => 
    api.get('/api/analytics/dashboard'),
};

export default api;