import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../../api/client';
import { useAuthContext } from '../../context/AuthContext';
import './Modal.css';

interface Company {
  id: string;
  name: string;
  cnpj: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active?: boolean;
  // O objeto completo da empresa que vem da lista de usuários
  company?: {
    id: string;
    name: string;
    cnpj: string;
  } | null;
}

interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  userToEdit?: User | null;
}

export function CreateUserModal({ isOpen, onClose, onSuccess, userToEdit }: CreateUserModalProps) {
  const { user } = useAuthContext();
  const [loading, setLoading] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'USER',
    company_cnpj: '' // <--- VOLTAMOS PARA CNPJ
  });

  const isSystemAdmin = user?.role === 'SYSTEM_ADMIN';
  const isEditing = !!userToEdit;

  // Carrega empresas ao abrir (Se for System Admin)
  useEffect(() => {
    if (isOpen && isSystemAdmin) {
      api.get('/companies/list')
        .then(response => {
          if (Array.isArray(response.data)) {
            setCompanies(response.data);
          } else if (response.data && Array.isArray(response.data.items)) {
            setCompanies(response.data.items);
          } else {
            setCompanies([]);
          }
        })
        .catch(error => {
          console.error("Erro ao buscar empresas:", error);
          setCompanies([]);
        });
    }
  }, [isOpen, isSystemAdmin]);

  // Preenche o formulário quando for Edição
  useEffect(() => {
    if (isOpen && userToEdit) {
      // Extrai o CNPJ para preencher o select
      let currentCnpj = '';
      if (userToEdit.company?.cnpj) {
        currentCnpj = userToEdit.company.cnpj;
      }

      setFormData({
        name: userToEdit.name || '',
        email: userToEdit.email || '',
        password: '', // Senha vazia na edição
        role: userToEdit.role || 'USER',
        company_cnpj: currentCnpj // <--- Preenche com o CNPJ
      });
    } else if (isOpen && !userToEdit) {
      // Reset para criação
      setFormData({ name: '', email: '', password: '', role: 'USER', company_cnpj: '' });
    }
  }, [isOpen, userToEdit]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      // Prepara o payload
      const payload: any = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        role: formData.role,
        // Envia o CNPJ se for System Admin
        company_cnpj: isSystemAdmin && formData.company_cnpj ? formData.company_cnpj : undefined
      };

      // Lógica de Senha
      if (!isEditing || (isEditing && formData.password.length > 0)) {
         payload.password = formData.password;
      }

      if (isEditing && userToEdit) {
        // --- ATUALIZAR (PUT) ---
        await api.put(`/users/update-user/${userToEdit.id}`, payload);
      } else {
        // --- CRIAR (POST) ---
        await api.post('/auth/register', payload);
      }

      onSuccess();
      onClose();

    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Erro ao salvar usuário.';
      alert(msg);
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">{isEditing ? 'Editar Usuário' : 'Novo Usuário'}</h2>
          <button onClick={onClose} className="close-button" type="button">
             <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          
          <div className="form-group">
            <label className="form-label">Nome</label>
            <input 
              className="form-input" required 
              value={formData.name}
              onChange={e => setFormData({...formData, name: e.target.value})} 
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input 
              type="email" className="form-input" required 
              value={formData.email}
              onChange={e => setFormData({...formData, email: e.target.value})} 
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              {isEditing ? 'Nova Senha (deixe em branco para manter)' : 'Senha'}
            </label>
            <input 
              type="password" 
              className="form-input" 
              required={!isEditing} 
              minLength={6}
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})} 
              placeholder={isEditing ? "******" : ""}
            />
          </div>

          {/* CAMPO DE EMPRESA (System Admin) */}
          {isSystemAdmin && (
            <div className="form-group">
              <label className="form-label">
                Empresa{formData.role === 'SYSTEM_ADMIN' ? ' (opcional para Super Admin)' : ' (Obrigatório)'}
              </label>
              <select
                className="form-select"
                required={formData.role !== 'SYSTEM_ADMIN'}
                value={formData.company_cnpj} // <--- Usa o CNPJ no value
                onChange={e => setFormData({...formData, company_cnpj: e.target.value})}
              >
                <option value="">Selecione uma empresa...</option>
                {companies.length === 0 && (
                  <option disabled>Carregando ou nenhuma empresa...</option>
                )}
                {companies.map(company => (
                  // IMPORTANTE: Aqui o value é o CNPJ
                  <option key={company.id} value={company.cnpj}>
                    {company.name} ({company.cnpj})
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Cargo</label>
            <select
              className="form-select"
              value={formData.role}
              onChange={e => setFormData({...formData, role: e.target.value})}
            >
              <option value="USER">Usuário Comum</option>
              <option value="MANAGER">Gerente</option>
              <option value="ADMIN">Administrador</option>
              {isSystemAdmin && <option value="SYSTEM_ADMIN">Super Admin (TI)</option>}
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Cancelar</button>
            <button 
                type="submit" 
                disabled={loading} 
                className="btn-primary"
            >
              {loading ? 'Salvando...' : (isEditing ? 'Atualizar' : 'Criar Usuário')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}