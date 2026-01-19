import type { UserRole } from '../constants/roles';

export interface MenuItem {
    label: string;
    path: string;
}

export const menuByRole: Record<UserRole, MenuItem[]> = {
    SYSTEM_ADMIN: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Usuários', path: '/users' },
        { label: 'Configurações', path: '/settings' },
        { label: 'Configurações de Sistema', path: '/system-settings' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Empresas', path: '/companies' },
    ],
    ADMIN: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Configurações', path: '/settings' },
        { label: 'Usuários', path: '/users' },
    ],
    MANAGER: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
    ],
    USER: [
        { label: 'Dashboard', path: '/dashboard' },
    ],
};