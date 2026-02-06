import { Routes, Route } from 'react-router-dom';
import Login from '../pages/Login/Login';
import Home from '../pages/Home/Home';
import Register from '../pages/Register/Register';
import MaintenancePage from '../pages/Maintenance/Maintenance';

export function PublicNavigation() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/home" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/maintenance" element={<MaintenancePage />} />

      {/* fallback */}
      <Route path="*" element={<Home />} />
    </Routes>
  );
}
