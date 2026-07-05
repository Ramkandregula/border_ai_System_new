import api from './api';
import { RiskAssessment } from '../types';

export const riskService = {
  calculateRisk: async (data: any): Promise<RiskAssessment> => {
    const response = await api.post('/api/risk/calculate', data);
    return response.data;
  },

  getHistory: async (personId?: number, skip: number = 0, limit: number = 100) => {
    const response = await api.get('/api/risk/history', {
      params: { person_id: personId, skip, limit },
    });
    return response.data;
  },

  getThreats: async () => {
    const response = await api.get('/api/risk/threats');
    return response.data;
  },
};
