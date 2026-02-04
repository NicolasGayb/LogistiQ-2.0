import React, { useState, useEffect } from 'react';
import { X, Save, Loader2 } from 'lucide-react';
import './Modal.css';

export interface ProductFormData {
  name: string;
  sku: string;
  price: number;
  quantity: number;
  description: string;
}

interface CreateProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: ProductFormData) => Promise<void>;
  initialData?: ProductFormData | null; // Aceita dados para edição
}

export default function CreateProductModal({ isOpen, onClose, onSave, initialData }: CreateProductModalProps) {
  const [loading, setLoading] = useState(false);
  
  const initialFormState = {
    name: '',
    sku: '',
    price: '',
    quantity: '',
    description: ''
  };

  const [formData, setFormData] = useState(initialFormState);

  // Se tiver initialData, preenche o form. Se não, limpa.
  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setFormData({
          name: initialData.name,
          sku: initialData.sku,
          price: String(initialData.price),
          quantity: String(initialData.quantity),
          description: initialData.description || ''
        });
      } else {
        setFormData(initialFormState);
      }
      setLoading(false);
    }
  }, [isOpen, initialData]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload: ProductFormData = {
        name: formData.name,
        sku: formData.sku,
        price: Number(formData.price),
        quantity: Number(formData.quantity),
        description: formData.description
      };

      await onSave(payload);
      onClose();
    } catch (error) {
      console.error('Erro ao salvar:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-content">
        <div className="modal-header">
          {/* Título dinâmico */}
          <h2 className="modal-title">
            {initialData ? 'Editar Produto' : 'Novo Produto'}
          </h2>
          <button className="close-button" onClick={onClose} title="Fechar">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Nome do Produto</label>
            <input
              type="text"
              className="form-input"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">SKU</label>
            <input
              type="text"
              className="form-input"
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              required
            />
          </div>

          <div className="form-group form-row">
            <div>
              <label className="form-label">Preço (R$)</label>
              <input
                type="number" step="0.01" min="0"
                className="form-input"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="form-label">Quantidade</label>
              <input
                type="number" min="0"
                className="form-input"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Descrição</label>
            <textarea
              className="form-input"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} style={{marginRight: 8}} />}
              {initialData ? 'Salvar Alterações' : 'Criar Produto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}