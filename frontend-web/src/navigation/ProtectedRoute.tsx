import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: JSX.Element;
  allowedRoles: Array<'SYSTEM_ADMIN' | 'ADMIN' | 'MANAGER' | 'USER'>;
}

const roleHierarchy = {
  SYSTEM_ADMIN: 4,
  ADMIN: 3,
  MANAGER: 2,
  USER: 1,
} as const;

export function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userLevel = roleHierarchy[user.role];
  const allowedLevels = allowedRoles.map((role) => roleHierarchy[role]);

  const hasAccess = allowedLevels.some(
    (level) => userLevel >= level
  );

  if (!hasAccess) {
    return <Navigate to="/forbidden" replace />;
  }

  return children;
}