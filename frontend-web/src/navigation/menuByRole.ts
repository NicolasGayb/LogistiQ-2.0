import type { UserRole } from '../constants/roles';

export interface MenuItem {
    label: string;
    path: string;
}

export const menuByRole: Record<UserRole, MenuItem[]> = {
    SYSTEM_ADMIN: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Usuários', path: '/users' },
        { label: 'Empresas', path: '/companies' },
        { label: 'Parceiros', path: '/partners' },
        { label: 'Produtos', path: '/products' },
        { label: 'Operações', path: '/operations' },
        { label: 'Configurações', path: '/settings' },
        { label: 'Configurações de Sistema', path: '/system-settings' },
    ],
    ADMIN: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Operações', path: '/operations' },
        { label: 'Parceiros', path: '/partners' },
        { label: 'Produtos', path: '/products' },
        { label: 'Usuários', path: '/users' },
        { label: 'Configurações', path: '/settings' },
    ],
    MANAGER: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Operações', path: '/operations' },
        { label: 'Parceiros', path: '/partners' },
        { label: 'Produtos', path: '/products' },
    ],
    USER: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Operações', path: '/operations' },
        { label: 'Produtos', path: '/products' },
    ],
};