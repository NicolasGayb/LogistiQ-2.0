import { Routes, Route, Navigate } from 'react-router-dom';
import { PrivateLayout } from '../layouts/PrivateLayout';
import { ProtectedRoute } from './ProtectedRoute';
import UsersPage from '../pages/Users/UsersPage';

import Dashboard from '../pages/Dashboard/dashboards/AdminDashboard';
import { SettingsPage } from '../pages/Settings/SettingsPage';
import ProductList from '../pages/Products/ProductList';
import OperationsPage from '../pages/Operations/OperationsPage';
import PartnerList from '../pages/Partners/PartnersList';

export function AdminNavigation() {
  return (
    <Routes>
      <Route
        element={
          <ProtectedRoute allowedRoles={['ADMIN', 'SYSTEM_ADMIN']}>
            <PrivateLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/partners" element={<PartnerList />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/products" element={<ProductList/>} />

        {/* fallback para evitar tela branca */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
