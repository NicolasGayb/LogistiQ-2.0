import '../Dashboard.css';

export default function AdminDashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Painel Administrativo</h1>
        <p className="dashboard-subtitle">
          Gestão de usuários e relatórios
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <span className="dashboard-card-title">Usuários Ativos</span>
          <span className="dashboard-card-value">—</span>
        </div>

        <div className="dashboard-card">
          <span className="dashboard-card-title">Relatórios</span>
          <span className="dashboard-card-value">—</span>
        </div>
      </div>
    </div>
  );
}
