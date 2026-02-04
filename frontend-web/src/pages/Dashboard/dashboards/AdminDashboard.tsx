import React, { useEffect, useState } from 'react';
import { 
  Users, 
  Package, 
  AlertTriangle, 
  FileText, 
  Settings,  
  Activity,
  Clock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../../../api/client';
import '../Dashboard.css'; 

// Interfaces
interface DashboardStat {
  total_users: number;
  active_users: number;
  stock_alerts: number;
  low_stock_items: number;
  recent_movements: number;
}

export default function AdminDashboard() {
  const navigate = useNavigate();

  // Estados
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState<DashboardStat>({
    total_users: 0,
    active_users: 0,
    stock_alerts: 0,
    low_stock_items: 0,
    recent_movements: 0,
  });

  // Busca de Dados
  useEffect(() => {
    async function fetchDashboardStats() {
      try {
        const response = await api.get('/dashboard/admin-stats');
        setStatsData(response.data);
      } catch (error) {
        console.error('Erro ao buscar estatísticas:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchDashboardStats();
  }, []);

  // Configuração dos Cards (Usando classes CSS para cores agora)
  const metricCards = [
    {
      label: 'Usuários Ativos',
      value: statsData.active_users,
      total: `de ${statsData.total_users} cadastrados`,
      icon: Users,
      variantClass: 'variant-primary', // Classe CSS definida no arquivo
    },
    {
      label: 'Alertas de Estoque',
      value: statsData.stock_alerts,
      total: 'Itens abaixo do mínimo',
      icon: AlertTriangle,
      variantClass: 'variant-danger', // Classe CSS
    },
    {
      label: 'Movimentações',
      value: statsData.recent_movements || 0,
      total: 'Últimos 30 dias',
      icon: Activity,
      variantClass: 'variant-info', // Classe CSS
    },
  ];

  return (
    <div className="dashboard-container">
      
      {/* --- HEADER --- */}
      <div className="dashboard-header dashboard-header-row">
        <div>
          <h1 className="dashboard-title">Visão Geral</h1>
          <p className="dashboard-subtitle">
            Acompanhe a performance e a equipe da sua empresa.
          </p>
        </div>
        <button className="btn-report" onClick={() => navigate('/relatorios')}>
            <FileText size={18} />
            Relatório Gerencial
        </button>
      </div>

      {/* --- KPIS (CARDS DE MÉTRICA) --- */}
      <div className="metrics-grid">
        {metricCards.map((stat, index) => (
          <div key={index} className="metric-card">
            <div className="metric-header">
                <span className="metric-title">{stat.label}</span>
                {/* A classe define a cor de fundo e do ícone */}
                <div className={`icon-box ${stat.variantClass}`}>
                    <stat.icon size={20} />
                </div>
            </div>
            
            {loading ? (
                <div className="skeleton-loader" />
            ) : (
                <div>
                    <span className="metric-value">{stat.value}</span>
                    <p className="metric-subtitle">{stat.total}</p>
                </div>
            )}
          </div>
        ))}
      </div>

      {/* --- GRID PRINCIPAL --- */}
      <div className="main-content-grid">
        
        {/* Lado Esquerdo: Ações Rápidas */}
        <div>
            <h2 className="section-title">Acesso Rápido</h2>
            <div className="actions-grid">
                
                <div className="action-card" onClick={() => navigate('/users')}>
                    <div className="action-icon-box variant-primary">
                        <Users size={24} />
                    </div>
                    <div className="action-info">
                        <h3>Gerenciar Equipe</h3>
                        <p>Adicionar ou remover acessos.</p>
                    </div>
                </div>

                <div className="action-card" onClick={() => navigate('/estoque')}>
                    <div className="action-icon-box variant-info">
                        <Package size={24} />
                    </div>
                    <div className="action-info">
                        <h3>Controle de Estoque</h3>
                        <p>Ajustar saldos e produtos.</p>
                    </div>
                </div>

                <div className="action-card" onClick={() => navigate('/settings')}>
                    <div className="action-icon-box variant-neutral">
                        <Settings size={24} />
                    </div>
                    <div className="action-info">
                        <h3>Configurações</h3>
                        <p>Dados da empresa e alertas.</p>
                    </div>
                </div>

            </div>
        </div>

        {/* Lado Direito: Atividade Recente */}
        <div>
            <h2 className="section-title">Atividade Recente</h2>
            <div className="activity-card">
                {[1, 2].map((_, i) => (
                    <div key={i} className="activity-item">
                        <div className="activity-icon-small">
                            <Clock size={16} />
                        </div>
                        <div>
                            <p className="activity-text">
                                <strong>Sistema</strong> realizou backup automático.
                            </p>
                            <span className="activity-time">Há 2 horas</span>
                        </div>
                    </div>
                ))}
                <div className="activity-footer">
                    Ver histórico completo
                </div>
            </div>
        </div>

      </div>
    </div>
  );
}