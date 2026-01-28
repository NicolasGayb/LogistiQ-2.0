import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../../api/client';
import './Modal.css';

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
    companyToEdit?: Company | null; // Para edição de empresa
}

export function CreateCompanyModal({ isOpen, onClose, onSuccess, companyToEdit }: CreateCompanyModalProps) {
  const [loading, setLoading] = useState(false);
  
  // Estado do formulário combinando com o Model
  const [formData, setFormData] = useState({
    name: '',
    cnpj: '',
    is_active: true // Padrão true conforme model
  });

  const isEditing = !!companyToEdit;

  useEffect(() => {
    if (isOpen && companyToEdit) {
      setFormData({
        name: companyToEdit.name,
        cnpj: companyToEdit.cnpj,
        is_active: companyToEdit.is_active
      });
    } else if (isOpen) {
      // Reset para criação
      setFormData({ name: '', cnpj: '', is_active: true });
    }
  }, [isOpen, companyToEdit]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEditing && companyToEdit) {
        // Atualizar
        await api.put(`/companies/${companyToEdit.id}`, formData);
      } else {
        // Criar (Token deve ser gerado no backend)
        await api.post('/companies', formData);
      }
      onSuccess();
      onClose();
    } catch (error: any) {
        const msg = error.response?.data?.detail || 'Erro ao salvar empresa.';
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
          <h2 className="modal-title">{isEditing ? 'Editar Empresa' : 'Nova Empresa'}</h2>
          <button onClick={onClose} className="close-button" type="button"><X size={24} /></button>
        </div>

        <form onSubmit={handleSubmit}>
          
          {/* NOME (Razão Social) */}
          <div className="form-group">
            <label className="form-label">Razão Social / Nome *</label>
            <input 
              className="form-input" required 
              value={formData.name}
              onChange={e => setFormData({...formData, name: e.target.value})} 
              placeholder="Ex: LogistiQ Soluções"
            />
          </div>

          {/* CNPJ */}
          <div className="form-group">
            <label className="form-label">CNPJ *</label>
            <input 
              className="form-input" required 
              value={formData.cnpj}
              onChange={e => setFormData({...formData, cnpj: e.target.value})} 
              placeholder="00.000.000/0001-00"
              maxLength={18} // Limite visual básico
            />
          </div>

          {/* STATUS (Aparece na edição ou criação para controle explícito) */}
          <div className="form-group checkbox-group" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '10px' }}>
            <input 
              type="checkbox"
              id="activeCheck"
              checked={formData.is_active}
              onChange={e => setFormData({...formData, is_active: e.target.checked})}
              style={{ width: '16px', height: '16px' }}
            />
            <label htmlFor="activeCheck" className="form-label" style={{ marginBottom: 0, cursor: 'pointer' }}>
              Empresa Ativa?
            </label>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Cancelar</button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Salvando...' : (isEditing ? 'Atualizar' : 'Salvar Empresa')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}