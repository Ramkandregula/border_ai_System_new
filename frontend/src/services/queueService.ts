import api from './api';
import { QueueEntry } from '../types';

export const queueService = {
  getStatus: async () => {
    const response = await api.get('/api/queue/status');
    return response.data;
  },

  listQueue: async (skip: number = 0, limit: number = 100) => {
    const response = await api.get('/api/queue', {
      params: { skip, limit },
    });
    return response.data;
  },

  addToQueue: async (data: any): Promise<QueueEntry> => {
    const response = await api.post('/api/queue/person', data);
    return response.data;
  },

  updateQueueEntry: async (id: number, data: any): Promise<QueueEntry> => {
    const response = await api.put(`/api/queue/${id}`, data);
    return response.data;
  },
};
