import { Routes, Route, Navigate } from 'react-router-dom';
import { PrivateLayout } from '../layouts/PrivateLayout';
import { ProtectedRoute } from './ProtectedRoute';

import Dashboard from '../pages/Dashboard/dashboards/SystemAdminDashboard';
import UsersPage from '../pages/Users/UsersPage';
import CompaniesPage from '../pages/Companies/CompaniesPage';
import { SettingsPage } from '../pages/Settings/SettingsPage';
import SystemSettings from '../pages/System/SystemSettings';
import ProductList from '../pages/Products/ProductList';
import OperationsPage from '../pages/Operations/OperationsPage';
import PartnerList from '../pages/Partners/PartnersList';

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
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/companies" element={<CompaniesPage />} />
        <Route path="/partners" element={<PartnerList />} />
        <Route path="/products" element={<ProductList />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/system-settings" element={<SystemSettings />} />
        {/* fallback para evitar tela branca */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
