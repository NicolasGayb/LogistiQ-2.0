import api from '../api/client';
import type { User } from '../types/user';

export async function getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
}

export async function logoutService(): Promise<void> {
    try {
        await api.post('/auth/logout');
    } catch (error) {
        console.warn('Logout error:', error);
    }
}