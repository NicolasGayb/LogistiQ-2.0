// Bibliotecas
import { useState, useEffect } from 'react';
import {
  Plus, Search, MoreVertical, Building2, CheckCircle, XCircle,
  Edit, Trash2, Clock, Key, Copy, Power, Ban
} from 'lucide-react';

// Componentes
import { Button } from '../../components/Button/Button';
import { Card } from '../../components/Card/Card';
import api from '../../api/client';
import { CreateCompanyModal } from '../../components/Modal/CreateCompanyModal';
import '../Users/UsersPage.css'; // Reutilizando estilos globais
import './CompaniesPage.css';

// Interface baseada estritamente no Model Python
interface Company {
  id: string;
  name: string;
  cnpj: string;
  is_active: boolean;
  updated_at?: string;
  token: string;
}

export default function CompaniesPage() {
    // Estados principais
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Estados de controle
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [companyToEdit, setCompanyToEdit] = useState<Company | null>(null);
    const [activeMenuId, setActiveMenuId] = useState<string | null>(null);

    // Busca empresas ao carregar a página
    useEffect(() => {
        fetchCompanies();
    }, []);

    // Fecha menu ao clicar fora
    useEffect(() => {
        const handleClickOutside = () => setActiveMenuId(null);
        if (activeMenuId) window.addEventListener('click', handleClickOutside);
        return () => window.removeEventListener('click', handleClickOutside);
    }, [activeMenuId]);

    // Função para buscar empresas
    async function fetchCompanies() {
        try {
            // Ajuste a rota conforme seu backend. Assumindo /companies ou /companies/list
            const response = await api.get('/companies/list'); 
            // Tratamento defensivo para listas paginadas ou diretas
            const data = Array.isArray(response.data) ? response.data : (response.data.items || []);
            setCompanies(data);
        } catch (error) {
            console.error('Erro ao buscar empresas:', error);
        } finally {
            setLoading(false);
        }
    }

    // Ações
    const toggleMenu = (id: string) => activeMenuId === id ? setActiveMenuId(null) : setActiveMenuId(id);
    const handleOpenCreate = () => { setCompanyToEdit(null); setIsModalOpen(true); };
    
    // Função de edição
    const handleEdit = (company: Company) => { 
        setActiveMenuId(null); 
        setCompanyToEdit(company); 
        setIsModalOpen(true); 
    };

    // Função de exclusão com confirmação
    const handleDelete = async (company: Company) => {
        setActiveMenuId(null);
        if (confirm(`ATENÇÃO: Deseja excluir a empresa ${company.name}? Isso pode apagar produtos vinculados.`)) {
            try {
                await api.delete(`/companies/${company.id}`);
                fetchCompanies();
            } catch (error) {
                alert('Erro ao excluir empresa.');
            }
        }
    };

    // Função utilitária para copiar o token
    const copyToken = (token: string) => {
        navigator.clipboard.writeText(token);
        alert('Token copiado para a área de transferência!');
    };

    // Formatação de data para exibição
    const formatDate = (dateString?: string) => {
        if (!dateString) return '—';
        return new Date(dateString).toLocaleDateString('pt-BR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    // Filtragem de empresas com base no termo de busca
    const filteredCompanies = companies.filter((c) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.cnpj.includes(searchTerm)
    );
    
    // Função para mascarar o token na exibição
    const maskToken = (token: string) => {
        if (!token || token.length <= 12) return token;
        return `${token.substring(0, 8)}••••••${token.substring(token.length - 4)}`;
    };

    // Função para ativar/desativar empresa
    const handleToggleStatus = async (company: Company) => {
        setActiveMenuId(null);
        
        // Verificação de qual ação tomar
        const action = company.is_active ? 'desativar' : 'ativar';
        // Mensagem de confirmação
        const confirmMessage = `Tem certeza que deseja ${action} a empresa ${company.name}?`;

        if (confirm(confirmMessage)) {
            try {
                // Chamada à API para alternar status
                const response = await api.patch(`/companies/toggle-company/${company.id}`, {});
                // Recarrega a lista após a ação
                fetchCompanies();
                // Mostra a mensagem de sucesso
                const successMsg = response.data.message || `Empresa ${action} com sucesso.`;
                alert(successMsg);

            // Tratamento de erro
            } catch (error: any) {
                const msg = error.response?.data?.detail || `Erro ao ${action} empresa.`;
                alert(msg);
                // Log detalhado para depuração
                console.error(error);
            }
        }
    };

    // Renderização do componente
    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Empresas</h1>
                    <p className="page-subtitle">Gerencie parceiros e integrações.</p>
                </div>
                <Button 
                    onClick={handleOpenCreate} 
                    className='bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors'
                >
                    <Plus size={18} /> Nova Empresa
                </Button>
            </header>

            {/* Barra de busca */}
            <div className="toolbar">
                <div className="search-box">
                    <Search size={18} className="search-icon" />
                    <input 
                        type="text" 
                        placeholder="Buscar por Nome ou CNPJ..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Tabela de empresas */}
            <Card noPadding className="table-card">
                {loading ? (
                    <div className="loading-state">Carregando...</div>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th style={{ width: '40%' }}>Empresa</th>
                                <th style={{ width: '30%' }}>Token de Acesso</th>
                                <th style={{ width: '20%' }}>Status & Data</th>
                                <th align="right" style={{ width: '10%' }}></th>
                            </tr>
                        </thead>
                        <tbody>
                        {filteredCompanies.length > 0 ? (
                            filteredCompanies.map((company) => (
                            <tr key={company.id} className="hover-row">
                                {/* 1. NOME & CNPJ */}
                                <td>
                                    <div className="user-info">
                                        <div className="user-avatar">
                                            <Building2 size={18} />
                                        </div>
                                        <div>
                                            <span className="user-name">{company.name}</span>
                                            <span className="user-email">CNPJ: {company.cnpj}</span>
                                        </div>
                                    </div>
                                </td>

                                {/* 2. TOKEN */}
                                <td style={{ verticalAlign: 'middle' }}>
                                    <div className='token-badge-container'>
                                        {/* Ícone de chave */}
                                        <Key size={14} className="text-slate-400 shrink-0" />

                                        {/* Valor Mascarado */}
                                        <span className="token-value" title="Token de Acesso (Mascarado)">
                                            {maskToken(company.token)}
                                        </span>

                                        {/* Divisor Vertical */}
                                        <div className="token-divider"></div>

                                        {/* Botão de Copiar */}
                                        <button 
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                copyToken(company.token);
                                            }}
                                            className="token-copy-btn"
                                            title="Copiar Token Completo"
                                        >
                                            <Copy size={14} />
                                        </button>
                                    </div>
                                </td>
                                
                                {/* 3. STATUS & DATA */}
                                <td>
                                    <div className="flex flex-col items-start gap-1">
                                        <div>
                                            {company.is_active ? 
                                                <span className="status-badge active inline-flex"><CheckCircle size={12} /> Ativa</span> : 
                                                <span className="status-badge inactive inline-flex"><XCircle size={12} /> Inativa</span>
                                            }
                                        </div>
                                        <div className="date-display">
                                            <Clock size={12} />
                                            <span>{formatDate(company.updated_at)}</span>
                                        </div>
                                    </div>
                                </td>

                                {/* 4. AÇÕES */}
                                <td align="right">
                                    <div className='action-wrapper'>
                                        <button className="action-btn" onClick={(e) => {e.stopPropagation(); toggleMenu(company.id);}}>
                                            <MoreVertical size={18} />
                                        </button>
                                        {activeMenuId === company.id && (
                                            <div className='dropdown-menu'>
                                                {/* Botão de edição */}
                                                <button className='dropdown-item' onClick={(e) => { 
                                                    e.stopPropagation(); handleEdit(company); 
                                                }}>
                                                    <Edit size={16} /> Editar
                                                </button>
                                                
                                                {/* Botão de ativar/desativar */}
                                                <button
                                                    className={`dropdown-item ${company.is_active ? 'danger' : 'success'}`}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleToggleStatus(company);
                                                    }}
                                                >
                                                    {company.is_active ? (
                                                        <><Ban size={16} /> Desativar</>
                                                    ) : (
                                                        <><Power size={16} /> Ativar</>
                                                    )}
                                                </button>

                                                <button className='dropdown-item danger' onClick={(e) => { 
                                                    e.stopPropagation(); handleDelete(company); 
                                                }}>
                                                    <Trash2 size={16} /> Excluir
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </td>
                            </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={4} className="empty-state">
                                    Nenhuma empresa encontrada.
                                </td>
                            </tr>
                        )}
                        </tbody>
                    </table>
                )}
            </Card>

            <CreateCompanyModal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)} 
                onSuccess={fetchCompanies} 
                companyToEdit={companyToEdit} 
            />
        </div>
    );
}