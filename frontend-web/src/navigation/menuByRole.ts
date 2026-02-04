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
        { label: 'Produtos', path: '/products' },
        { label: 'Configurações', path: '/settings' },
        { label: 'Configurações de Sistema', path: '/system-settings' },
    ],
    ADMIN: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Produtos', path: '/products' },
        { label: 'Usuários', path: '/users' },
        { label: 'Configurações', path: '/settings' },
    ],
    MANAGER: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Relatórios', path: '/reports' },
        { label: 'Produtos', path: '/products' },
    ],
    USER: [
        { label: 'Dashboard', path: '/dashboard' },
        { label: 'Produtos', path: '/products' },
    ],
};