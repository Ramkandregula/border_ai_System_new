import api from './api';
import { Person } from '../types';

export const detectionService = {
  getStatus: async () => {
    const response = await api.get('/api/detection/status');
    return response.data;
  },

  listPersons: async (skip: number = 0, limit: number = 100) => {
    const response = await api.get('/api/detection/persons', {
      params: { skip, limit },
    });
    return response.data;
  },

  getPerson: async (id: number): Promise<Person> => {
    const response = await api.get(`/api/detection/person/${id}`);
    return response.data;
  },

  createDetection: async (data: any): Promise<Person> => {
    const response = await api.post('/api/detection/person', data);
    return response.data;
  },

  updatePerson: async (id: number, data: any): Promise<Person> => {
    const response = await api.put(`/api/detection/person/${id}`, data);
    return response.data;
  },
};
