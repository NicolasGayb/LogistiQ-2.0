import '../Dashboard.css';

export default function ManagerDashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Indicadores</h1>
        <p className="dashboard-subtitle">
          Acompanhamento operacional
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <span className="dashboard-card-title">Relatórios</span>
          <span className="dashboard-card-value">—</span>
        </div>

        <div className="dashboard-card">
          <span className="dashboard-card-title">Status</span>
          <span className="dashboard-card-value">—</span>
        </div>
      </div>
    </div>
  );
}
