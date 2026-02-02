import { Routes, Route, Navigate } from 'react-router-dom';
import { PrivateLayout } from '../layouts/PrivateLayout';
import { ProtectedRoute } from './ProtectedRoute';

import Dashboard from '../pages/Dashboard/dashboards/SystemAdminDashboard';
import UsersPage from '../pages/Users/UsersPage';
import CompaniesPage from '../pages/Companies/CompaniesPage';
import { SettingsPage } from '../pages/Settings/SettingsPage';

export function SystemAdminNavigation() {
  return (
    <Routes>
      <Route
        element={
          <ProtectedRoute allowedRoles={['SYSTEM_ADMIN']}>
            <PrivateLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/users" element={<UsersPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/companies" element={<CompaniesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        {/* fallback para evitar tela branca */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
