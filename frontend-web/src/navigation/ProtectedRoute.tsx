import { Navigate } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import type { UserRole } from '../constants/roles';
import { ROLE_HIERARCHY } from '../constants/roles';
import type { JSX } from 'react';

interface ProtectedRouteProps {
  children: JSX.Element;
  allowedRoles: UserRole[];
}

export function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { user, loading } = useAuthContext();

  if (loading) {
    return <div>Carregando...</div>;
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

  return children;
}