import api from './api';
import { AuthResponse, User } from '../types';

export const authService = {
  login: async (username: string, password: string): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/login', { username, password });
    return response.data;
  },

  register: async (userData: any): Promise<User> => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/auth/logout');
  },

  refreshToken: async (token: string): Promise<AuthResponse> => {
    const response = await api.post('/api/auth/refresh', { token });
    return response.data;
  },
};
