import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../../api/client';
import './Modal.css';

// Tipagem da Empresa e Props do Componente
interface Company {
  id: string;
  name: string;
  cnpj: string;
  is_active: boolean;
}

interface CreateCompanyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  companyToEdit?: Company | null;
}

export function CreateCompanyModal({ isOpen, onClose, onSuccess, companyToEdit }: CreateCompanyModalProps) {
  const [loading, setLoading] = useState(false);
  
  const isEditing = !!companyToEdit;

  // Estado Unificado
  const [formData, setFormData] = useState({
    // Dados da Empresa
    name: '',
    cnpj: '',
    is_active: true,
    // Dados do Admin (Só usados na criação)
    admin_name: '',
    admin_email: '',
    admin_password: ''
  });

  useEffect(() => {
    if (isOpen && companyToEdit) {
      // Modo Edição: Só preenche dados da empresa
      setFormData(prev => ({
        ...prev,
        name: companyToEdit.name,
        cnpj: companyToEdit.cnpj,
        is_active: companyToEdit.is_active,
        admin_name: '', admin_email: '', admin_password: '' // Limpa dados sensíveis
      }));
    } else if (isOpen) {
      // Modo Criação: Limpa tudo
      setFormData({ 
        name: '', cnpj: '', is_active: true,
        admin_name: '', admin_email: '', admin_password: ''
      });
    }
  }, [isOpen, companyToEdit]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEditing && companyToEdit) {
        // --- PUT (Edição) ---
        // Na edição só enviamos os dados da empresa
        const payloadEdit = {
            name: formData.name,
            cnpj: formData.cnpj,
            is_active: formData.is_active
        };
        await api.put(`/companies/${companyToEdit.id}`, payloadEdit);
      
      } else {
        // --- POST (Criação) ---
        // Formato esperado pela API para criação de empresa + admin
        const payloadCreate = {
            company: {
                name: formData.name,
                cnpj: formData.cnpj,
                is_active: formData.is_active
            },
            admin_name: formData.admin_name,
            admin_email: formData.admin_email,
            admin_password: formData.admin_password
        };
        
        await api.post('/companies/', payloadCreate);
      }
      
      onSuccess();
      onClose();
    } catch (error: any) {
        // Log para ajudar a debugar erro 422
        console.error("Erro no envio:", error.response?.data);
        const msg = error.response?.data?.detail || 'Erro ao processar solicitação.';
        // Se o erro for uma lista tenta pegar a primeira mensagem
        const alertMsg = Array.isArray(msg) ? msg[0].msg : msg;
        alert(alertMsg);
    } finally {
      setLoading(false);
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">{isEditing ? 'Editar Empresa' : 'Criação de Empresa'}</h2>
          <button onClick={onClose} className="close-button" type="button"><X size={24} /></button>
        </div>

        <form onSubmit={handleSubmit}>
          
          {/* SEÇÃO 1: DADOS DA EMPRESA */}
          <div className="mb-4">
             <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Dados da Empresa</h3>
             
             <div className="form-group">
                <label className="form-label">Razão Social *</label>
                <input 
                  className="form-input" required 
                  value={formData.name}
                  onChange={e => handleChange('name', e.target.value)} 
                  placeholder="Ex: LogistiQ Soluções"
                />
             </div>

             <div className="form-group">
                <label className="form-label">CNPJ *</label>
                <input 
                  className="form-input" 
                  required 
                  value={formData.cnpj}
                  onChange={e => handleChange('cnpj', e.target.value)} 
                  placeholder="00.000.000/0001-00"
                  maxLength={18}
                  disabled={isEditing}
                  style={isEditing ? {backgroundColor: '#f1f5f9', color: '#94a3b8', cursor: 'not-allowed' } : {}}
                />
             </div>
          </div>

          {/* SEÇÃO 2: DADOS DO ADMIN (SÓ APARECE NA CRIAÇÃO) */}
          {!isEditing && (
              <div className="mb-4 pt-4 border-t border-slate-100">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Administrador da Empresa</h3>
                
                <div className="form-group">
                    <label className="form-label">Nome do Admin *</label>
                    <input 
                        className="form-input" required 
                        value={formData.admin_name}
                        onChange={e => handleChange('admin_name', e.target.value)} 
                        placeholder="João da Silva"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">E-mail de Acesso *</label>
                    <input 
                        type="email"
                        className="form-input" required 
                        value={formData.admin_email}
                        onChange={e => handleChange('admin_email', e.target.value)} 
                        placeholder="joao@empresa.com"
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Senha Inicial *</label>
                    <input 
                        type="password"
                        className="form-input" required 
                        value={formData.admin_password}
                        onChange={e => handleChange('admin_password', e.target.value)} 
                        placeholder="***********"
                        minLength={6}
                    />
                </div>
              </div>
          )}

          {/* CHECKBOX DE STATUS */}
          <div className="form-group checkbox-group">
            <input 
              type="checkbox"
              id="activeCheck"
              checked={formData.is_active}
              onChange={e => handleChange('is_active', e.target.checked)}
            />
            <label htmlFor="activeCheck">Empresa Ativa?</label>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Cancelar</button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Processando...' : (isEditing ? 'Atualizar Empresa' : 'Criar Empresa')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}