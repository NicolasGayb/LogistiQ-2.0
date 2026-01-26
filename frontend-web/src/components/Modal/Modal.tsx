import { useState, useEffect } from 'react';
import api from '../../api/client';
import { useAuthContext } from '../../context/AuthContext';
import './Modal.css';

interface Company {
  id: number;
  name: string;
}

interface CreateUserModalProps {
  isOpen: boolean; // Controla se o modal está aberto
  onClose: () => void; // Função para fechar o modal
  onSuccess: () => void; // Recarrega a lista de usuários após criação
}

export function CreateUserModal({ isOpen, onClose, onSuccess }: CreateUserModalProps) {
  const { user } = useAuthContext(); // Pega o usuário logado do contexto
  const [loading, setLoading] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]); // Lista de empresas para o select
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'USER',
    company_id: '', // Campo para empresa (só SYSTEM_ADMIN preenche)
  });

  // Se for SYSTEM_ADMIN, busca as empresas assim que o modal abrir
  useEffect(() => {
    if (isOpen && user?.role === 'SYSTEM_ADMIN') {
      api.get('/companies')
        .then(response => setCompanies(response.data))
        .catch(error => console.error("Erro ao buscar empresas:", error));
    }
  }, [isOpen, user]);

  if (!isOpen) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      // Payload de criação de usuário
      const payload = {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        role: formData.role,
        // Só envia o company_id se for SYSTEM_ADMIN. 
        // Se for outro, o backend ignora ou pega do token.
        company_id: user?.role === 'SYSTEM_ADMIN' ? Number(formData.company_id) : undefined
      };

      await api.post('/auth/register', payload);

      onSuccess();
      onClose();
      // Reset do form
      setFormData({ name: '', email: '', password: '', role: 'USER', company_id: '' });

    } catch (error) {
      alert('Erro ao criar usuário. Verifique os dados.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  const isSystemAdmin = user?.role === 'SYSTEM_ADMIN';

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">Novo Usuário</h2>
          <button onClick={onClose} className="close-button">&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          
          {/* ... Campos Nome, Email e Senha ... */}
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
            <label className="form-label">Senha</label>
            <input 
              type="password" className="form-input" required minLength={6}
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})} 
            />
          </div>

          {/* CAMPO DE EMPRESA (Só aparece para SYSTEM_ADMIN) */}
          {isSystemAdmin && (
            <div className="form-group">
              <label className="form-label">Empresa (Obrigatório)</label>
              <select
                className="form-select"
                required={isSystemAdmin} // HTML valida se é obrigatório
                value={formData.company_id}
                onChange={e => setFormData({...formData, company_id: e.target.value})}
              >
                <option value="">Selecione uma empresa...</option>
                {companies.map(company => (
                  <option key={company.id} value={company.id}>
                    {company.name}
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
            <button type="submit" disabled={loading} className="btn-primary" style={{backgroundColor: '#10b981', color:'white', padding:'8px 16px', borderRadius:'6px'}}>
              {loading ? 'Salvando...' : 'Criar Usuário'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}