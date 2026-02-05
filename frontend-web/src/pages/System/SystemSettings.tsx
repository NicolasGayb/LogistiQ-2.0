import { useState, useEffect } from 'react';
import { 
  Settings, Shield, Activity, Save, Server, Database, 
  Globe, RefreshCw, Lock, Loader2, AlertTriangle
} from 'lucide-react';
import { SystemService, type AuditLog, type SystemStats, type SystemSettingsData } from '../../services/systemService';
import './SystemSettings.css';

type TabOption = 'general' | 'logs' | 'monitor';

export default function SystemSettings() {
  const [activeTab, setActiveTab] = useState<TabOption>('general');
  const [loading, setLoading] = useState(false); // Loading do botão salvar
  const [dataLoading, setDataLoading] = useState(false); // Loading para buscar dados

  // --- STATES REAIS ---
  
  // Configurações Gerais (Agora alinhado com o Backend: snake_case)
  const [generalSettings, setGeneralSettings] = useState<SystemSettingsData>({
    maintenance_mode: false,
    allow_registrations: true,
    session_timeout: 60
  });

  // Dados reais de Logs e Status
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStats | null>(null);

  // --- EFEITOS (Busca de Dados) ---

  useEffect(() => {
    if (activeTab === 'general') {
      loadGeneralSettings();
    } else if (activeTab === 'logs') {
      loadLogs();
    } else if (activeTab === 'monitor') {
      loadStats();
    }
  }, [activeTab]);

  // --- FUNÇÕES DE CARREGAMENTO ---

  const loadGeneralSettings = async () => {
    try {
      const data = await SystemService.getSettings();
      if (data) {
        setGeneralSettings(data);
      }
    } catch (error) {
      console.error('Erro ao buscar configurações gerais', error);
    }
  };

  const loadLogs = async () => {
    setDataLoading(true);
    try {
      const data = await SystemService.getAuditLogs();
      setAuditLogs(data);
    } catch (error) {
      console.error('Erro ao buscar logs', error);
    } finally {
      setDataLoading(false);
    }
  };

  const loadStats = async () => {
    setDataLoading(true);
    try {
      const data = await SystemService.getStats();
      setSystemStatus(data);
    } catch (error) {
      console.error('Erro ao buscar status', error);
    } finally {
      setDataLoading(false);
    }
  };

  // --- FUNÇÃO DE SALVAR ---

  const handleSaveGeneral = async () => {
    setLoading(true);
    try {
      await SystemService.updateSettings(generalSettings);
      alert('Configurações globais atualizadas com sucesso!');
    } catch (error) {
      console.error(error);
      alert('Erro ao salvar as configurações. Verifique o console.');
    } finally {
      setLoading(false);
    }
  };

  // --- RENDERIZADORES ---

  const renderGeneralTab = () => (
    <div className="tab-content fade-in">
      <div className="settings-card">
        <div className="card-header">
          <h3>Controles de Acesso e Segurança</h3>
          <p>Defina como a plataforma se comporta para todos os usuários.</p>
        </div>
        
        <div className="settings-grid">
          {/* Modo Manutenção */}
          <div className="setting-item">
            <div className="setting-info">
              <div className="setting-label">
                <Lock size={18} className="text-red-500" />
                <span>Modo Manutenção</span>
              </div>
              <p className="setting-desc">
                Bloqueia o acesso de todos os usuários (exceto Admins).
              </p>
            </div>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={generalSettings.maintenance_mode}
                onChange={e => setGeneralSettings({...generalSettings, maintenance_mode: e.target.checked})}
              />
              <span className="slider"></span>
            </label>
          </div>

          {/* Novos Cadastros */}
          <div className="setting-item">
            <div className="setting-info">
              <div className="setting-label">
                <Globe size={18} className="text-blue-500" />
                <span>Permitir Novos Cadastros</span>
              </div>
              <p className="setting-desc">
                Se desativado, a página de "Criar Conta" ficará indisponível.
              </p>
            </div>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={generalSettings.allow_registrations}
                onChange={e => setGeneralSettings({...generalSettings, allow_registrations: e.target.checked})}
              />
              <span className="slider"></span>
            </label>
          </div>

          {/* Tempo de Sessão */}
          <div className="setting-item">
            <div className="setting-info">
              <div className="setting-label">
                <Activity size={18} className="text-slate-500" />
                <span>Tempo Limite de Sessão (min)</span>
              </div>
              <p className="setting-desc">Desconecta usuários inativos após este período.</p>
            </div>
            <input 
              type="number" 
              className="input-number"
              value={generalSettings.session_timeout}
              onChange={e => setGeneralSettings({...generalSettings, session_timeout: Number(e.target.value)})}
            />
          </div>
        </div>

        <div className="card-footer">
          <button className="btn-save" onClick={handleSaveGeneral} disabled={loading}>
            {loading ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
            Salvar Alterações
          </button>
        </div>
      </div>
    </div>
  );

  const renderLogsTab = () => (
    <div className="tab-content fade-in">
      <div className="settings-card">
        <div className="card-header">
          <h3>Logs de Auditoria</h3>
          <p>Rastreamento das últimas atividades críticas no sistema.</p>
        </div>
        
        {dataLoading ? (
          <div className="p-8 text-center text-slate-500">
             <Loader2 className="animate-spin mx-auto mb-2" size={32} />
             Carregando auditoria...
          </div>
        ) : (
          <div className="table-responsive">
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Ação</th>
                  <th>Usuário</th>
                  <th>IP</th>
                  <th>Data/Hora</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.length === 0 ? (
                  <tr><td colSpan={5} className="p-4 text-center text-slate-500">Nenhum log encontrado.</td></tr>
                ) : (
                  auditLogs.map(log => (
                    <tr key={log.id}>
                      <td>
                        <span className={`status-dot ${log.status}`} title={log.status}></span>
                      </td>
                      <td className="font-medium">
                          {log.action}
                          {log.description && <div className="text-xs text-slate-400 font-normal">{log.description}</div>}
                      </td>
                      <td>{log.user}</td>
                      <td className="font-mono text-sm">{log.ip}</td>
                      <td className="text-sm text-slate-500">{log.date}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
        
        <div className="card-footer text-center">
          <button className="btn-link" onClick={loadLogs}>Atualizar Lista</button>
        </div>
      </div>
    </div>
  );

  const renderMonitorTab = () => {
    if (dataLoading || !systemStatus) {
        return (
            <div className="p-12 text-center text-slate-500">
                <Loader2 className="animate-spin mx-auto mb-3" size={40} />
                Verificando saúde do sistema...
            </div>
        )
    }

    return (
      <div className="tab-content fade-in">
        <div className="monitor-grid">
          
          {/* API Status */}
          <div className="monitor-card">
            <div className="monitor-icon bg-green-100 text-green-600">
              <Server size={24} />
            </div>
            <div className="monitor-info">
              <h4>Backend API</h4>
              <span className={`status-badge ${systemStatus.api_status === 'online' ? 'online' : 'error'}`}>
                {systemStatus.api_status === 'online' ? 'Online' : 'Offline'}
              </span>
            </div>
            <div className="monitor-metric">
              <small>Ops Totais: {systemStatus.metrics.total_operations}</small>
            </div>
          </div>

          {/* DB Status */}
          <div className="monitor-card">
            <div className="monitor-icon bg-blue-100 text-blue-600">
              <Database size={24} />
            </div>
            <div className="monitor-info">
              <h4>PostgreSQL</h4>
              <span className={`status-badge ${systemStatus.db_status === 'online' ? 'online' : 'error'}`}>
                 {systemStatus.db_status === 'online' ? 'Online' : 'Offline'}
              </span>
            </div>
            <div className="monitor-metric">
              <small>Conexões: {systemStatus.metrics.active_connections}</small>
            </div>
          </div>

          {/* SLA / Atrasos */}
          <div className="monitor-card">
            <div className="monitor-icon bg-yellow-100 text-yellow-600">
              <AlertTriangle size={24} />
            </div>
            <div className="monitor-info">
              <h4>SLA de Entrega</h4>
              <span className={`status-badge ${systemStatus.metrics.delayed_operations > 0 ? 'warning' : 'online'}`}>
                {systemStatus.metrics.delayed_operations > 0 ? 'Atenção' : 'Normal'}
              </span>
            </div>
            <div className="monitor-metric">
              <small>Atrasos: {systemStatus.metrics.delayed_operations}</small>
            </div>
          </div>

        </div>

        <div className="settings-card mt-6">
          <div className="card-header flex justify-between items-center">
            <h3>Informações do Ambiente</h3>
            <button onClick={loadStats} className="text-emerald-600 hover:text-emerald-800" title="Atualizar">
                <RefreshCw size={18} />
            </button>
          </div>
          <div className="env-info-grid">
            <div className="env-item">
              <span className="env-label">Versão do Sistema</span>
              <span className="env-value">{systemStatus.version}</span>
            </div>
            <div className="env-item">
              <span className="env-label">Ambiente</span>
              <span className="env-value">Production</span>
            </div>
            <div className="env-item">
              <span className="env-label">Status Geral</span>
              <span className="env-value text-emerald-600">Operacional</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="system-settings-container">
      <div className="page-header mb-6">
        <h1 className="page-title">Configurações de Sistema</h1>
        <p className="page-subtitle">Painel de controle global do administrador.</p>
      </div>

      {/* TABS NAVIGATION */}
      <div className="tabs-nav">
        <button 
          className={`tab-btn ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
        >
          <Settings size={18} />
          Geral
        </button>
        <button 
          className={`tab-btn ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          <Shield size={18} />
          Auditoria
        </button>
        <button 
          className={`tab-btn ${activeTab === 'monitor' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitor')}
        >
          <Activity size={18} />
          Monitoramento
        </button>
      </div>

      {/* TABS CONTENT */}
      <div className="tabs-body">
        {activeTab === 'general' && renderGeneralTab()}
        {activeTab === 'logs' && renderLogsTab()}
        {activeTab === 'monitor' && renderMonitorTab()}
      </div>
    </div>
  );
}