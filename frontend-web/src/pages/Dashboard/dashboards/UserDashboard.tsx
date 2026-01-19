import '../Dashboard.css';

export default function UserDashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Bem-vindo</h1>
        <p className="dashboard-subtitle">
          Suas informações no sistema
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <span className="dashboard-card-title">Minhas Atividades</span>
          <span className="dashboard-card-value">—</span>
        </div>
      </div>
    </div>
  );
}
