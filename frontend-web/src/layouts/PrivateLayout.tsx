import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar/Sidebar';
import { Header } from '../components/Header/Header'; 
import './PrivateLayout.css';

export function PrivateLayout() {
  return (
    <div className="layout-container">
      {/* 1. Menu Lateral Fixo */}
      <aside className="layout-sidebar">
        <Sidebar />
      </aside>

      {/* 2. Área Principal */}
      <div className="layout-main">
        {/* Cabeçalho do topo (opcional) */}
        <Header /> 

        {/* 3. Conteúdo Variável (Aqui é onde UsersPage e Dashboard aparecem!) */}
        <main className="layout-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}