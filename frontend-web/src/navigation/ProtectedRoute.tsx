import { Navigate, Outlet } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import { ROLE_HIERARCHY } from '../constants/roles';
import type { UserRole } from '../constants/roles';
import type { ReactNode } from 'react';

interface ProtectedRouteProps {
  children?: ReactNode;
  allowedRoles: UserRole[];
}

export function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { user, loading } = useAuthContext();

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>Carregando sessão...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userLevel = ROLE_HIERARCHY[user.role];
  const hasAccess = allowedRoles.some(
    (role) => userLevel >= ROLE_HIERARCHY[role]
  );

  if (!hasAccess) {
    return <Navigate to="/forbidden" replace />;
  }

  // Se tiver filho, renderiza ele.
  // Se não, renderiza Outlet (rota aninhada padrão do v6).
  return children ? <>{children}</> : <Outlet />;
}