import api from './api';
import { DashboardStats } from '../types';

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  },

  getAnalytics: async () => {
    const response = await api.get('/api/dashboard/analytics');
    return response.data;
  },

  getAlerts: async () => {
    const response = await api.get('/api/dashboard/alerts');
    return response.data;
  },
};
