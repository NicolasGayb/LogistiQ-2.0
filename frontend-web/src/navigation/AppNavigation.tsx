import { useAuthContext } from '../context/AuthContext';

import { PublicNavigation } from './PublicNavigation';
import { SystemAdminNavigation } from './SystemAdminNavigation';
import { AdminNavigation } from './AdminNavigation';
import { ManagerNavigation } from './ManagerNavigation';
import { UserNavigation } from './UserNavigation';
import Forbidden from '../pages/Forbidden';

export function AppNavigation() {
  const { user, loading, isAuthenticated } = useAuthContext();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <span>Loading...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <PublicNavigation />;
  }

  switch (user?.role) {
    case 'SYSTEM_ADMIN':
      return <SystemAdminNavigation />;

    case 'ADMIN':
      return <AdminNavigation />;

    case 'MANAGER':
      return <ManagerNavigation />;

    case 'USER':
      return <UserNavigation />;

    default:
      return <Forbidden />;
  }
}
