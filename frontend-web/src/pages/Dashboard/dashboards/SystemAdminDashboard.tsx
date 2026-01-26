import { useNavigate } from 'react-router-dom';
import { 
  Building2, 
  Users, 
  Activity, 
  Settings, 
  FileText, 
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

// --- Imports dos componentes ---
import { Card } from '../../../components/Card/Card'; 
import { Button } from '../../../components/Button/Button';
import api from '../../../api/client';
import { useEffect } from 'react';
import '../Dashboard.css';
import { useState } from 'react';

// --- Tipagem e Interfaces (Clean Code: TypeScript Strict) ---

interface KpiMetric {
  id: string;
  label: string;
  value: string | number;
  icon: React.ElementType;
  status?: 'success' | 'warning' | 'error' | 'neutral';
}

interface QuickAction {
  id: string;
  label: string;
  description: string;
  path: string;
  icon: React.ElementType;
}

interface DashboardStatsResponse {
  companies_count: number;
  users_count: number;
  system_status: string;
}

export default function SystemAdminDashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await api.get('/companies/stats');
        setStats(response.data);
      } catch (err) {
        console.error('Erro ao buscar estatísticas do dashboard:', err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  // 1. Definição de Dados (Separado da View)

  const metrics: KpiMetric[] = [
    { 
      id: 'companies', 
      label: 'Empresas Ativas', 
      value: stats ? stats.companies_count : 'Carregando...', 
      icon: Building2, 
      status: 'neutral' 
    },
    { 
      id: 'users', 
      label: 'Usuários Totais', 
      value: stats ? stats.users_count : 'Carregando...', 
      icon: Users, 
      status: 'neutral' 
    },
    { 
      id: 'health', 
      label: 'Status do Sistema', 
      value: loading ? '...' : (error ? 'Erro' : stats ? stats.system_status : 'Desconhecido'),
      icon: Activity, 
      status: error ? 'error' : 'success'
    },
  ];

  // 2. Ações baseadas no menu da Sidebar
  const actions: QuickAction[] = [
    {
      id: 'btn-companies',
      label: 'Gerenciar Empresas',
      description: 'Cadastrar ou bloquear parceiros.',
      path: '/companies',
      icon: Building2
    },
    {
      id: 'btn-users',
      label: 'Controle de Usuários',
      description: 'Gestão de acessos e permissões.',
      path: '/users',
      icon: Users
    },
    {
      id: 'btn-sys-settings',
      label: 'Configurações de Sistema',
      description: 'Variáveis globais e ambiente.',
      path: '/system-settings',
      icon: Settings
    },
    {
      id: 'btn-reports',
      label: 'Relatórios de Auditoria',
      description: 'Logs de acesso e segurança.',
      path: '/reports',
      icon: FileText
    }
  ];

  // --- Renderização ---
  return (
    <div className="dashboard-container fade-in">
      
      {/* SEÇÃO 1: Header da Página */}
      <header className="dashboard-header-section">
        <div>
          <h1 className="title-lg">Visão Geral</h1>
          <p className="text-muted">Painel de controle do Administrador do Sistema</p>
        </div>
        {/* Exemplo de uso do seu componente Button */}
        <div className="header-actions">
           <Button onClick={() => window.location.reload()}>
              Atualizar Dados
           </Button>
        </div>
      </header>

      {/* SEÇÃO 2: Métricas (KPIs) */}
      <section className="metrics-grid">
        {metrics.map((metric) => (
          // Usando seu componente Card para envolver as métricas
          <Card key={metric.id} className="metric-card">
            <div className="metric-header">
              <span className="metric-label">{metric.label}</span>
              <metric.icon size={20} className="metric-icon" />
            </div>
            <div className={`metric-value status-${metric.status}`}>
              {metric.value}
            </div>
          </Card>
        ))}
      </section>

      {/* SEÇÃO 3: Grid Principal (Ações e Logs) */}
      <div className="main-content-grid">
        
        {/* Coluna Esquerda: Acesso Rápido */}
        <div className="content-column">
          <h2 className="section-title">Acesso Rápido</h2>
          <div className="actions-grid">
            {actions.map((action) => (
              // Reutilizando Card como botão interativo
              <Card 
                key={action.id} 
                className="action-card cursor-pointer"
                onClick={() => navigate(action.path)} // Navegação programática
              >
                <div className="action-icon-box">
                  <action.icon size={24} />
                </div>
                <div className="action-info">
                  <h3>{action.label}</h3>
                  <p>{action.description}</p>
                </div>
                <div className="action-arrow">
                  <ArrowRight size={16} />
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Coluna Direita: Painel de Atividade */}
        <div className="content-column">
          <div className="flex-between">
            <h2 className="section-title">Alertas do Sistema</h2>
            <Button variant="outline" size="sm" onClick={() => navigate('/logs')}>
              Ver tudo
            </Button>
          </div>
          
          <Card className="logs-panel">
            <div className="empty-state">
              <ShieldAlert size={32} className="text-muted" />
              <p>Nenhum incidente de segurança nas últimas 24h.</p>
            </div>
          </Card>
        </div>

      </div>
    </div>
  );
}