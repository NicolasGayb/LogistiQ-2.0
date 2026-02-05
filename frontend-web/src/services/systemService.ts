import api from '../api/client';

export interface AuditLog {
    id: string;
    action: string;
    user: string;
    ip: string;
    date: string;
    timestamp: string;
    status: 'success' | 'warning' | 'error';
    description?: string;
}

export interface SystemStats {
    api_status: string;
    db_status: string;
    email_service: string;
    version: string;
    metrics: {
        total_operations: number;
        delayed_operations: number;
        active_connections: number;
    };
}

export interface SystemSettingsData {
    maintenance_mode: boolean;
    session_timeout: number;
    allow_registrations: boolean;
}

export const SystemService = {
    // Busca os logs de auditoria do sistema
    getAuditLogs: async () => {
        const response = await api.get<AuditLog[]>('/system-admins/audit-logs');
        return response.data;
    },

    // Busca o status do sistema
    getStats: async () => {
        const response = await api.get<SystemStats>('/system-admins/stats');
        return response.data;
    },

    // Busca as configurações do sistema
    getSettings: async () => {
        const response = await api.get<SystemSettingsData>('/system-admins/settings');
        return response.data;
    },

    // Atualiza as configurações do sistema
    updateSettings: async (settings: SystemSettingsData) => {
        const response = await api.put<SystemSettingsData>('/system-admins/settings', settings);
        return response.data;
    }
};