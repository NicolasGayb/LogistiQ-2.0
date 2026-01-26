import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  MoreVertical,
  Building2,
  CheckCircle,
  XCircle,
  User as UserIcon,
} from 'lucide-react';

// --- Imports dos componentes ---
import { Button } from '../../components/Button/Button';
import { Card } from '../../components/Card/Card';
import api from '../../api/client';
import { CreateUserModal } from '../../components/Modal/Modal'; 
import './UsersPage.css';

// --- Tipagem (TypeScript) ---
interface User {
  id: string;
  name: string;
  email: string;
  role: 'SYSTEM_ADMIN' | 'ADMIN' | 'MANAGER' | 'USER';
  is_active: boolean;
  company?: {
    id: string;
    name: string;
  } | null;
}

// --- O COMPONENTE DA PÁGINA (Export Default) ---
export default function UsersPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    
    // 1. ESTADO PARA CONTROLAR O MODAL
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    // Busca de dados no backend
    useEffect(() => {
        fetchUsers();
    }, []);

    async function fetchUsers() {
        try {
            // setLoading(true); // Opcional: mostrar loading visual ao recarregar
            const response = await api.get('/users');
            setUsers(response.data);
        } catch (error) {
            console.error('Erro ao buscar usuários:', error);
        } finally {
            setLoading(false);
        }
    }

    // Lógica de Filtro (Busca)
    const safeUsers = Array.isArray(users) ? users : [];
    const filteredUsers = safeUsers.filter((user) =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.company && user.company.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    // Componente interno para as Badges (Cargos)
    const RoleBadge = ({ role }: { role: string }) => {
        const roles: Record<string, { label: string; class: string }> = {
            SYSTEM_ADMIN: { label: 'Administrador do Sistema', class: 'badge-purple' },
            ADMIN: { label: 'Administrador', class: 'badge-blue' },
            MANAGER: { label: 'Gerente', class: 'badge-orange' },
            USER: { label: 'Usuário', class: 'badge-gray' },
        };

        const config = roles[role] || { label: 'Desconhecido', class: 'badge-gray' };

        return (
            <span className={`role-badge ${config.class}`}>
                {config.label}
            </span>
        );
    };

    return (
        <div className="page-container fade-in">
        
            {/* HEADER */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Usuários</h1>
                    <p className="page-subtitle">Gerencie o acesso e permissões da plataforma.</p>
                </div>
                
                {/* 2. BOTÃO QUE ABRE O MODAL */}
                <Button 
                    onClick={() => setIsCreateModalOpen(true)} 
                    className='bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors'
                >
                    <Plus size={18} />
                    Novo Usuário
                </Button>
            </header>

            {/* BARRA DE BUSCA */}
            <div className="toolbar">
                <div className="search-box">
                    <Search size={18} className="search-icon" />
                    <input 
                        type="text" 
                        placeholder="Buscar usuário..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* TABELA DE DADOS */}
            <Card noPadding className="table-card">
                {loading ? (
                    <div className="loading-state">Carregando...</div>
                ) : (
                    <table className="data-table">
                        <thead>
                        <tr>
                            <th>Usuário</th>
                            <th>Cargo</th>
                            <th>Empresa</th>
                            <th>Status</th>
                            <th align="right"></th>
                        </tr>
                        </thead>
                        <tbody>
                        {filteredUsers.length > 0 ? (
                            filteredUsers.map((user) => (
                            <tr key={user.id}>
                                <td>
                                    <div className="user-info">
                                        <div className="user-avatar">
                                            <UserIcon size={18} />
                                        </div>
                                        <div>
                                            <span className="user-name">{user.name}</span>
                                            <span className="user-email">{user.email}</span>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <RoleBadge role={user.role} />
                                </td>
                                <td>
                                    <div className="company-info">
                                        {user.company ? (
                                        <>
                                            <Building2 size={14} />
                                            <span>{user.company.name}</span>
                                        </>
                                        ) : (
                                        <span className="text-muted" title="Sem empresa (Super Admin)">—</span>
                                        )}
                                    </div>
                                </td>
                                <td>
                                    {user.is_active ? (
                                        <span className="status-badge active">
                                            <CheckCircle size={12} /> Ativo
                                        </span>
                                    ) : (
                                        <span className="status-badge inactive">
                                            <XCircle size={12} /> Inativo
                                        </span>
                                    )}
                                </td>
                                <td align="right">
                                    <button className="action-btn">
                                        <MoreVertical size={18} />
                                    </button>
                                </td>
                            </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={5} className="empty-state">
                                    Nenhum usuário encontrado.
                                </td>
                            </tr>
                        )}
                        </tbody>
                    </table>
                )}
            </Card>

            {/* 3. MODAL (INVISÍVEL ATÉ SER CHAMADO) */}
            <CreateUserModal 
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)} // Fecha o modal
                onSuccess={() => {
                    fetchUsers(); // 4. Recarrega a tabela quando criar com sucesso
                }}
            />

        </div>
    );
}