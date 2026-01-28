import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  MoreVertical,
  Building2,
  CheckCircle,
  XCircle,
  User as UserIcon,
  Edit, 
  Trash2,
  Power,
  Ban, Calendar, Clock
} from 'lucide-react';

// --- Imports dos componentes ---
import { Button } from '../../components/Button/Button';
import { Card } from '../../components/Card/Card';
import api from '../../api/client';
import { CreateUserModal } from '../../components/Modal/Modal';
import { useAuthContext } from '../../context/AuthContext'; // Importante para saber quem é o admin
import './UsersPage.css';

// --- Tipagem (TypeScript) ---
interface User {
  id: string;
  name: string;
  email: string;
  role: 'SYSTEM_ADMIN' | 'ADMIN' | 'MANAGER' | 'USER';
  is_active: boolean;
  updated_at?: string;
  company?: {
    id: string;
    name: string;
    cnpj: string;
  } | null;
}

// --- O COMPONENTE DA PÁGINA (Export Default) ---
export default function UsersPage() {
    const { user: currentUser } = useAuthContext(); // Pegamos o usuário logado para verificar permissões
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Estados do Modal e Edição
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [userToEdit, setUserToEdit] = useState<User | null>(null);

    // Estado do Menu Dropdown
    const [activeMenuUserId, setActiveMenuUserId] = useState<string | null>(null);

    // Carregar usuários ao montar o componente
    useEffect(() => {
        fetchUsers();
    }, []);

    // Fechar o menu ao clicar fora
    useEffect(() => {
        const handleClickOutside = () => setActiveMenuUserId(null);
        if (activeMenuUserId) {
            window.addEventListener('click', handleClickOutside);
        }
        return () => window.removeEventListener('click', handleClickOutside);
    }, [activeMenuUserId]);

    async function fetchUsers() {
        try {
            const response = await api.get('/users');
            setUsers(response.data);
        } catch (error) {
            console.error('Erro ao buscar usuários:', error);
        } finally {
            setLoading(false);
        }
    }

    // --- AÇÕES DO MENU ---

    const toggleMenu = (userId: string) => {
        if (activeMenuUserId === userId) {
            setActiveMenuUserId(null); 
        } else {
            setActiveMenuUserId(userId); 
        }
    };

    // 1. ABRIR MODAL DE CRIAÇÃO
    const handleOpenCreate = () => {
        setUserToEdit(null); // Limpa edição
        setIsModalOpen(true);
    };

    // 2. ABRIR MODAL DE EDIÇÃO
    const handleEditUser = (targetUser: User) => {
        setActiveMenuUserId(null);
        setUserToEdit(targetUser); // Passa os dados para o modal
        setIsModalOpen(true);
    };

    // 3. ATIVAR / DESATIVAR USUÁRIO (Sua rota PATCH)
    const handleToggleStatus = async (targetUser: User) => {
        setActiveMenuUserId(null);
        
        const action = targetUser.is_active ? 'desativar' : 'ativar';
        const confirmMessage = `Tem certeza que deseja ${action} o acesso de ${targetUser.name}?`;

        if (confirm(confirmMessage)) {
            try {
                // Chama a rota específica que você criou
                await api.patch(`/users/toggle-user/${targetUser.id}`, {});
                fetchUsers(); // Recarrega a lista para atualizar o ícone
            } catch (error) {
                alert('Erro ao alterar status do usuário. Verifique suas permissões.');
                console.error(error);
            }
        }
    };

    // 4. EXCLUIR USUÁRIO (DELETE)
    const handleDeleteUser = async (targetUser: User) => {
        setActiveMenuUserId(null);
        
        if (confirm(`ATENÇÃO: Deseja excluir PERMANENTEMENTE o usuário ${targetUser.name}?`)) {
            try {
                await api.delete(`/users/delete-user/${targetUser.id}`);
                fetchUsers(); // Recarrega a lista se der certo
                alert(`Usuário ${targetUser.name} excluído com sucesso (ele não tinha histórico).`);
            } catch (error: any) {
                // Se o backend mandar o erro 409 (Conflict), mostramos a mensagem bonita
                if (error.response && error.response.status === 409) {
                    alert(`Não é possível excluir o usuário ${targetUser.name} porque ele possui referências no sistema (ex: registros de atividades). Considere desativá-lo em vez disso.`); 
                } else {
                    // Erro genérico
                    alert('Erro ao excluir usuário.');
                    console.error(error);
                }
            }
        } 
    };
    const formatDate = (dateString?: string) => {
        if (!dateString) return '—';
        return new Date(dateString).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    
    // --- FILTROS E RENDERIZAÇÃO ---

    const safeUsers = Array.isArray(users) ? users : [];
    const filteredUsers = safeUsers.filter((user) =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.company && user.company.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const RoleBadge = ({ role }: { role: string }) => {
        const roles: Record<string, { label: string; class: string }> = {
            SYSTEM_ADMIN: { label: 'Administrador do Sistema', class: 'badge-purple' },
            ADMIN: { label: 'Administrador', class: 'badge-blue' },
            MANAGER: { label: 'Gerente', class: 'badge-orange' },
            USER: { label: 'Usuário', class: 'badge-gray' },
        };
        const config = roles[role] || { label: 'Desconhecido', class: 'badge-gray' };
        return <span className={`role-badge ${config.class}`}>{config.label}</span>;
    };

    return (
        <div className="page-container fade-in">
        
            {/* HEADER */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Usuários</h1>
                    <p className="page-subtitle">Gerencie o acesso e permissões da plataforma.</p>
                </div>
                
                <Button 
                    onClick={handleOpenCreate} // Usa a nova função que limpa o userToEdit
                    className='bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors'
                >
                    <Plus size={18} />
                    Novo Usuário
                </Button>
            </header>

            {/* TOOLBAR */}
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

            {/* TABELA */}
            <Card noPadding className="table-card">
                {loading ? (
                    <div className="loading-state">Carregando...</div>
                ) : (
                    <table className="data-table">
                        <thead>
                        <tr>
                            <th style={{ width: '40%' }}>Usuário</th>
                            <th style={{ width: '30%' }}>Cargo & Empresa</th>
                            <th style={{ width: '20%' }}>Status & Atualização</th>
                            <th align='right' style={{ width: '10%' }}></th> {/* Coluna para ações */}
                        </tr>
                        </thead>
                        <tbody>
                        {/* -- RENDERIZAÇÃO DOS USUÁRIOS -- */}
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
                                {/* CARGO E EMPRESA */}
                                <td>
                                    <div className="flex flex-col gap-1">
                                        {/* Cargo com destaque */}
                                        <RoleBadge role={user.role} />
                                        
                                        {/* Empresa menor, embaixo */}
                                        <div className="company-info-compact">
                                            {user.company ? (
                                                <>
                                                    <Building2 size={12} />
                                                    <span>{user.company.name}</span>
                                                </>
                                            ) : (
                                                <span className="text-muted text-xs">— Global</span>
                                            )}
                                        </div>
                                    </div>
                                </td>
                                {/* STATUS E DATA DE ATUALIZAÇÃO */}
                                <td>
                                    <div className="flex flex-col items-start gap-1">
                                        {/* Badge de Status */}
                                        <div>
                                            {user.is_active ? 
                                                <span className="status-badge active inline-flex"><CheckCircle size={12} /> Ativo</span> : 
                                                <span className="status-badge inactive inline-flex"><XCircle size={12} /> Inativo</span>
                                            }
                                        </div>
                                        
                                        {/* Data com visual de "pill" (pílula) cinza */}
                                        <div className="date-display" title="Última atualização">
                                            <Clock size={12} />
                                            <span>{formatDate(user.updated_at)}</span>
                                        </div>
                                    </div>
                                </td>
                                {/* AÇÕES (MENU DROPDOWN) */}
                                <td align="right">
                                    <div className='action-wrapper'>
                                        <button className="action-btn" onClick={(e) => {e.stopPropagation(); toggleMenu(user.id);}}>
                                            <MoreVertical size={18} />
                                        </button>

                                        {activeMenuUserId === user.id && (
                                            <div className='dropdown-menu'>
                                                {/* 1. EDITAR */}
                                                <button className='dropdown-item' onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleEditUser(user);
                                                }}>
                                                    <Edit size={16} /> Editar
                                                </button>
                                                
                                                {/* 2. ATIVAR / DESATIVAR */}
                                                <button 
                                                    className={`dropdown-item ${user.is_active ? 'danger' : 'success'}`}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleToggleStatus(user);
                                                    }}
                                                >
                                                    {user.is_active ? (
                                                        <><Ban size={16} /> Desativar</>
                                                    ) : (
                                                        <><Power size={16} /> Ativar</>
                                                    )}
                                                </button>

                                                {/* 3. EXCLUIR (Só aparece para SYSTEM_ADMIN) */}
                                                {currentUser?.role === 'SYSTEM_ADMIN' && (
                                                    <button className='dropdown-item danger' onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDeleteUser(user);
                                                    }}>
                                                        <Trash2 size={16} /> Excluir
                                                    </button>
                                                )}
                                            </div>
                                        )}
                                    </div>
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

            {/* MODAL DE CRIAÇÃO / EDIÇÃO */}
            <CreateUserModal 
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={() => {
                    fetchUsers(); // Recarrega a tabela ao salvar
                }}
                userToEdit={userToEdit} // Passamos o usuário selecionado (ou null)
            />

        </div>
    );
}