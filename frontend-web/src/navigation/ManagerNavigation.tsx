import { Routes, Route, Navigate } from 'react-router-dom';
import { PrivateLayout } from '../layouts/PrivateLayout';
import { ProtectedRoute } from './ProtectedRoute';

import Dashboard from '../pages/Dashboard/dashboards/ManagerDashboard';
import { SettingsPage } from '../pages/Settings/SettingsPage';
import OperationsPage from '../pages/Operations/OperationsPage';
import PartnerList from '../pages/Partners/PartnersList';

export function ManagerNavigation() {
  return (
    <Routes>
      <Route
        element={
          <ProtectedRoute allowedRoles={['MANAGER', 'ADMIN', 'SYSTEM_ADMIN']}>
            <PrivateLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/partners" element={<PartnerList />} />
        <Route path="/settings" element={<SettingsPage />} />
        {/* fallback para evitar tela branca */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
