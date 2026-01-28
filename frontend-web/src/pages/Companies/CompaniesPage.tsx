import { useState, useEffect } from 'react';
import {
  Plus, Search, MoreVertical, Building2, CheckCircle, XCircle,
  Edit, Trash2, Clock, Key, Copy
} from 'lucide-react';

import { Button } from '../../components/Button/Button';
import { Card } from '../../components/Card/Card';
import api from '../../api/client';
import { CreateCompanyModal } from '../../components/Modal/CreateCompanyModal';
import '../Users/UsersPage.css'; // Reutilizando estilos globais

// Interface baseada estritamente no seu Model Python
interface Company {
  id: string;
  name: string;
  cnpj: string;
  is_active: boolean;
  created_at: string;
  token: string;
}

export default function CompaniesPage() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Estados
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [companyToEdit, setCompanyToEdit] = useState<Company | null>(null);
    const [activeMenuId, setActiveMenuId] = useState<string | null>(null);

    useEffect(() => {
        fetchCompanies();
    }, []);

    // Fecha menu ao clicar fora
    useEffect(() => {
        const handleClickOutside = () => setActiveMenuId(null);
        if (activeMenuId) window.addEventListener('click', handleClickOutside);
        return () => window.removeEventListener('click', handleClickOutside);
    }, [activeMenuId]);

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
    
    const handleEdit = (company: Company) => { 
        setActiveMenuId(null); 
        setCompanyToEdit(company); 
        setIsModalOpen(true); 
    };

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

    const formatDate = (dateString?: string) => {
        if (!dateString) return '—';
        return new Date(dateString).toLocaleDateString('pt-BR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    const filteredCompanies = companies.filter((c) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.cnpj.includes(searchTerm)
    );

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

                                {/* 2. TOKEN (Novo campo do Model) */}
                                <td>
                                    <div className="flex items-center gap-2 bg-slate-50 p-2 rounded border border-slate-200 w-fit max-w-[200px]">
                                        <Key size={14} className="text-slate-400 shrink-0" />
                                        <span className="text-xs text-slate-600 truncate select-all font-mono">
                                            {company.token}
                                        </span>
                                        <button 
                                            onClick={() => copyToken(company.token)}
                                            className="text-slate-400 hover:text-blue-500 transition-colors"
                                            title="Copiar Token"
                                        >
                                            <Copy size={12} />
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
                                            <span>{formatDate(company.created_at)}</span>
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
                                                <button className='dropdown-item' onClick={(e) => { 
                                                    e.stopPropagation(); handleEdit(company); 
                                                }}>
                                                    <Edit size={16} /> Editar
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