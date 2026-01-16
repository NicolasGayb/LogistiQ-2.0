import { Routes, Route } from 'react-router-dom';
import Login from '../pages/Login';

export function PublicNavigation() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="*" element={<Login />} />
    </Routes>
  );
}
