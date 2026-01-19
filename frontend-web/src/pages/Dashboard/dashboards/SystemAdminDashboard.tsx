import '../Dashboard.css';

export default function SystemAdminDashboard() {
  return (
    <div className="dashboard">
      {/* HEADER */}
      <div>
        <h1 className="dashboard-title">Visão Geral</h1>
        <p className="dashboard-subtitle">
          Acompanhamento operacional da plataforma
        </p>
      </div>

      {/* STATUS */}
      <div className="dashboard-status">
        <div className="status-card">
          <span className="status-title">Empresas ativas</span>
          <span className="status-value">—</span>
        </div>

        <div className="status-card">
          <span className="status-title">Usuários</span>
          <span className="status-value">—</span>
        </div>

        <div className="status-card">
          <span className="status-title">Sistema</span>
          <span className="status-value" style={{ color: '#16a34a' }}>
            Operacional
          </span>
        </div>
      </div>

      {/* MAIN */}
      <div className="dashboard-main">
        <div className="panel">
          <h2 className="panel-title">Atividade recente</h2>
          <p className="panel-muted">
            Nenhuma movimentação registrada.
          </p>
        </div>

        <div className="panel">
          <h2 className="panel-title">Resumo</h2>
          <p className="panel-muted">
            Dados gerais do sistema aparecerão aqui.
          </p>
        </div>
      </div>
    </div>
  );
}
