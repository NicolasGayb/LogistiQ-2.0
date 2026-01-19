import { useAuthContext } from '../../context/AuthContext';
import type { UserRole } from '../../constants/roles';

import SystemAdminDashboard from './dashboards/SystemAdminDashboard';
import AdminDashboard from './dashboards/AdminDashboard';
import ManagerDashboard from './dashboards/ManagerDashboard';
import UserDashboard from './dashboards/UserDashboard';
import type { JSX } from 'react/jsx-dev-runtime';

export function Dashboard() {
  const { user } = useAuthContext();

  if (!user) return null;

  const dashboardsByRole: Record<UserRole, JSX.Element> = {
    SYSTEM_ADMIN: <SystemAdminDashboard />,
    ADMIN: <AdminDashboard />,
    MANAGER: <ManagerDashboard />,
    USER: <UserDashboard />,
  };

  return dashboardsByRole[user.role];
}