import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import './DashboardLayout.css';

export default function DashboardLayout({ children }) {
  return (
    <div className="layout">
      <Sidebar />

      <div className="layout-content">
        <Header />
        <main className="layout-main">
          {children}
        </main>
      </div>
    </div>
  );
}