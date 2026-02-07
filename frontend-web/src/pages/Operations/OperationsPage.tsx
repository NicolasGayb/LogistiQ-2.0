import { useState, useEffect } from 'react';
import { 
  Plus, Filter, Calendar, AlertCircle, ArrowDownCircle, ArrowUpCircle, 
  MoreVertical, Clock, Truck, Package 
} from 'lucide-react';
import api from '../../api/client';
import './OperationsPage.css';

// --- TIPAGENS ---
interface Operation {
  id: string;
  operation_number: string | null;
  type: 'DELIVERY' | 'PICKUP' | 'TRANSFER' | 'RETURN';
  status: string;
  partner?: { name: string }; // ? pois pode ser nulo no banco
  origin?: string;
  destination?: string;
  expected_delivery_date: string;
  total_value: number;
}

interface KPI {
  pending: number;
  late: number;
  completed_today: number;
}

// --- CONFIGURAÇÃO DE STATUS (Granular) ---
const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  CREATED:     { label: 'Criado',        color: '#4b5563', bg: '#f3f4f6' }, // Gray
  AT_ORIGIN:   { label: 'Na Origem',     color: '#d97706', bg: '#fffbeb' }, // Amber
  LOADED:      { label: 'Carregado',     color: '#b45309', bg: '#fef3c7' }, // Dark Amber
  IN_TRANSIT:  { label: 'Em Trânsito',   color: '#2563eb', bg: '#eff6ff' }, // Blue
  AT_HUB:      { label: 'No Hub',        color: '#7c3aed', bg: '#f5f3ff' }, // Violet
  UNLOADED:    { label: 'Descarregado',  color: '#0891b2', bg: '#ecfeff' }, // Cyan
  DELIVERED:   { label: 'Entregue',      color: '#166534', bg: '#dcfce7' }, // Green
  COMPLETED:   { label: 'Concluído',     color: '#15803d', bg: '#dcfce7' }, // Green
  CANCELED:    { label: 'Cancelado',     color: '#991b1b', bg: '#fee2e2' }, // Red
};

export default function OperationsPage() {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [kpis, setKpis] = useState<KPI>({ pending: 0, late: 0, completed_today: 0 });
  const [loading, setLoading] = useState(true);

  // Estados de Filtro
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  // Busca dados ao carregar ou mudar filtros
  useEffect(() => {
    fetchData();
  }, [statusFilter, typeFilter, dateFilter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fazemos as duas requisições em paralelo para ser mais rápido
      const [kpiRes, listRes] = await Promise.all([
        api.get('/operations/kpis'),
        api.get('/operations', { 
          params: { 
            status: statusFilter || undefined, 
            type: typeFilter || undefined,
            start_date: dateFilter || undefined // Assume que o filtro é data de inicio
          } 
        })
      ]);
      setKpis(kpiRes.data);
      setOperations(listRes.data);
    } catch (error) {
      console.error("Erro ao carregar operações:", error);
    } finally {
      setLoading(false);
    }
  };

  // --- HELPERS VISUAIS ---

  const renderStatusBadge = (statusKey: string) => {
    const config = STATUS_CONFIG[statusKey] || STATUS_CONFIG.CREATED;
    return (
      <span style={{ 
        backgroundColor: config.bg, 
        color: config.color,
        padding: '0.35rem 0.75rem',
        borderRadius: '999px',
        fontSize: '0.75rem',
        fontWeight: 700,
        whiteSpace: 'nowrap',
        display: 'inline-block'
      }}>
        {config.label}
      </span>
    );
  };

  const checkSLA = (dateString: string, status: string) => {
    // Se já terminou, não tem atraso
    if (['DELIVERED', 'COMPLETED', 'CANCELED'].includes(status)) return null;
    
    const expected = new Date(dateString);
    const now = new Date();
    
    // Zera as horas para comparar apenas datas
    now.setHours(0,0,0,0); expected.setHours(0,0,0,0);

    if (now > expected) {
      return (
        <span className="sla-badge sla-late">
          <AlertCircle size={14} strokeWidth={2.5} /> ATRASADO
        </span>
      );
    }
    return <span className="sla-badge sla-ok text-gray-400 font-normal">No prazo</span>;
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <div className="ops-container">
      {/* 1. Header */}
      <div className="ops-header">
        <div className="ops-title">
          <h1>Painel de Operações</h1>
          <p>Visão geral de entradas, saídas e movimentações logísticas.</p>
        </div>
        <button className="btn-new-op">
          <Plus size={20} /> Nova Operação
        </button>
      </div>

      {/* 2. KPIs (Cards) */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon bg-amber-50 text-amber-600 border border-amber-100">
            <Package size={28} />
          </div>
          <div className="kpi-content">
            <h3>Pendentes Ativos</h3>
            <div className="kpi-value">{kpis.pending}</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon bg-red-50 text-red-600 border border-red-100">
            <Clock size={28} />
          </div>
          <div className="kpi-content">
            <h3>Atrasados (SLA)</h3>
            <div className="kpi-value text-red-600">{kpis.late}</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon bg-emerald-50 text-emerald-600 border border-emerald-100">
            <Truck size={28} />
          </div>
          <div className="kpi-content">
            <h3>Concluídos Hoje</h3>
            <div className="kpi-value text-emerald-600">{kpis.completed_today}</div>
          </div>
        </div>
      </div>

      {/* 3. Barra de Filtros */}
      <div className="filters-bar">
        <div className="filter-label">
          <Filter size={18} /> Filtros:
        </div>
        
        <select 
          className="filter-select"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option value="">Todos os Tipos</option>
          <option value="DELIVERY">Entrada (Compra)</option>
          <option value="PICKUP">Saída (Venda)</option>
          <option value="TRANSFER">Transferência</option>
          <option value="RETURN">Devolução</option>
        </select>

        <select 
          className="filter-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">Todos os Status</option>
          <option value="CREATED">Criado</option>
          <option value="IN_TRANSIT">Em Trânsito</option>
          <option value="AT_HUB">No Hub</option>
          <option value="DELIVERED">Entregue</option>
          <option value="CANCELED">Cancelado</option>
          <option value="COMPLETED">Concluído</option>
          <option value="AT_ORIGIN">Na Origem</option>
          <option value="LOADED">Carregado</option>
          <option value="UNLOADED">Descarregado</option>
        </select>

        <div className="relative">
            <input 
              type="date" 
              className="filter-input pl-10" 
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
            <Calendar size={16} className="absolute left-3 top-3 text-gray-400 pointer-events-none"/>
        </div>

        {/* Botão limpar filtros (aparece só se tiver filtro ativo) */}
        {(statusFilter || typeFilter || dateFilter) && (
          <button 
            onClick={() => { setStatusFilter(''); setTypeFilter(''); setDateFilter(''); }}
            className="text-sm text-red-600 hover:text-red-800 font-medium ml-auto"
          >
            Limpar Filtros
          </button>
        )}
      </div>

      {/* 4. Tabela de Dados */}
      <div className="table-wrapper">
        <table className="ops-table">
          <thead>
            <tr>
              <th style={{ width: '120px' }}>Código</th>
              <th style={{ width: '140px' }}>Tipo</th>
              <th>Parceiro / Rota</th>
              <th>Previsão & SLA</th>
              <th>Valor Total</th>
              <th>Status Atual</th>
              <th style={{ width: '50px' }}></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
               <tr><td colSpan={7} className="text-center py-12 text-gray-500">Carregando operações...</td></tr>
            ) : operations.length === 0 ? (
               <tr><td colSpan={7} className="text-center py-12 text-gray-500">Nenhuma operação encontrada para os filtros selecionados.</td></tr>
            ) : (
              operations.map((op) => (
                <tr key={op.id}>
                  {/* Código Visual */}
                  <td>
                    <span className="op-number">{op.operation_number || 'OP-####'}</span>
                  </td>
                  
                  {/* Tipo com Ícone */}
                  <td>
                    {op.type === 'DELIVERY' ? (
                      <span className="type-indicator type-delivery">
                        <ArrowDownCircle size={18} /> Entrada
                      </span>
                    ) : (
                      <span className="type-indicator type-pickup">
                        <ArrowUpCircle size={18} /> Saída
                      </span>
                    )}
                  </td>
                  
                  {/* Parceiro e Rota */}
                  <td>
                    <div className="flex flex-col">
                      <span className="font-bold text-gray-900">{op.partner?.name || 'Cliente Final'}</span>
                      <span className="text-xs text-gray-500">
                        {op.origin || '?'} ➝ {op.destination || '?'}
                      </span>
                    </div>
                  </td>
                  
                  {/* Data e SLA */}
                  <td>
                    <div className="sla-container">
                      <span className="sla-date">{formatDate(op.expected_delivery_date)}</span>
                      {checkSLA(op.expected_delivery_date, op.status)}
                    </div>
                  </td>
                  
                  {/* Valor */}
                  <td className="font-mono font-medium text-gray-700">
                    {formatCurrency(op.total_value)}
                  </td>
                  
                  {/* Status Badge */}
                  <td>
                    {renderStatusBadge(op.status)}
                  </td>
                  
                  {/* Ações */}
                  <td className="text-right">
                    <button className="btn-icon" title="Ver Detalhes">
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}