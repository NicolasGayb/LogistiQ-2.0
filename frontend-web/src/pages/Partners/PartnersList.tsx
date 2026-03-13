import { useState, useEffect } from 'react';
import { 
  Plus, Search, Filter, Edit, Trash2, MapPin, Building2, User, ArrowRight 
} from 'lucide-react';
import api from '../../api/client';
import { CreatePartnerModal } from '../../components/Modal/CreatePartnerModal';
import './PartnersList.css';

// Interface conforme retorno do Backend
interface Partner {
  id: string;
  name: string;
  document: string;
  email?: string;
  phone?: string;
  city: string;
  state: string;
  address?: string;
  is_customer: boolean;
  is_supplier: boolean;
  active: boolean;
  company_id: string;
}

export default function PartnersList() {
  
  // Estados de Dados
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(true);

  // Estados de UI (Modal e Filtros)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL'); // ALL, CUSTOMER, SUPPLIER
  const [editingPartner, setEditingPartner] = useState<Partner | null>(null);
  
  // Paginação
  const [page, setPage] = useState(0);
  const LIMIT = 10;

  // Efeito de Busca (com Debounce para não floodar a API)
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchPartners();
    }, 500); // Espera 500ms após parar de digitar

    return () => clearTimeout(delayDebounce);
  }, [searchTerm, typeFilter, page]);

  const fetchPartners = async () => {
    setLoading(true);
    try {
      const response = await api.get('/partners/', {
        params: {
          skip: page * LIMIT,
          limit: LIMIT,
          search: searchTerm || undefined,
          type: typeFilter !== 'ALL' ? typeFilter : undefined,
          active: true // Traz apenas ativos por padrão
        }
      });

      // Blindagem: Garante array
      if (Array.isArray(response.data)) {
        setPartners(response.data);
      } else {
        setPartners([]);
      }
    } catch (error) {
      console.error("Erro ao buscar parceiros:", error);
      setPartners([]);
    } finally {
      setLoading(false);
    }
  };

  // --- HELPERS VISUAIS ---
  
  // Formata CPF ou CNPJ
  const formatDocument = (doc: string) => {
    if (!doc) return '-';
    const cleaned = doc.replace(/\D/g, '');
    
    if (cleaned.length === 11) { // CPF
      return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    } else if (cleaned.length >= 12) { // CNPJ
      return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return doc;
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Não navega para edição
    if (confirm("Tem certeza que deseja excluir/desativar este parceiro?")) {
      try {
        await api.delete(`/partners/${id}`);
        fetchPartners(); // Recarrega
      } catch (error: any) {
        alert(error.response?.data?.detail || "Erro ao excluir.");
      }
    }
  };

  return (
    <div className="partners-container">
      
      {/* 1. HEADER */}
      <div className="partners-header">
        <div>
          <h1>Parceiros</h1>
          <p className="text-slate-500 text-sm mt-1">Gerencie clientes e fornecedores.</p>
        </div>
        <button className="btn-primary" onClick={() => { setEditingPartner(null); setIsModalOpen(true); }}>
          <Plus size={20} /> Novo Parceiro
        </button>
      </div>

      {/* 2. FILTROS */}
      <div className="filters-container">
        {/* Busca */}
        <div className="search-wrapper">
          <Search className="search-icon" size={18} />
          <input 
            type="text" 
            placeholder="Buscar por Nome, CPF ou CNPJ..." 
            className="form-input-search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Tipo Dropdown */}
        <div className="flex items-center gap-2">
          <Filter size={18} className="text-slate-400" />
          <select 
            className="form-select-filter"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="ALL">Todos os Tipos</option>
            <option value="CUSTOMER">Apenas Clientes</option>
            <option value="SUPPLIER">Apenas Fornecedores</option>
          </select>
        </div>
      </div>

      {/* 3. TABELA DE DADOS */}
      <div className="table-container">
        <table className="partners-table">
          <thead>
            <tr>
              <th>Nome / Razão Social</th>
              <th>Classificação</th>
              <th>Documento</th>
              <th>Cidade / UF</th>
              <th style={{ textAlign: 'right' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="text-center p-8 text-slate-500">Carregando parceiros...</td></tr>
            ) : partners.length === 0 ? (
              <tr><td colSpan={5} className="text-center p-8 text-slate-500">Nenhum parceiro encontrado.</td></tr>
            ) : (
              partners.map((partner) => (
                <tr 
                  key={partner.id} 
                  onClick={() => { setEditingPartner(partner); setIsModalOpen(true); }}
                  title="Clique para editar"
                >
                  {/* Nome */}
                  <td style={{ fontWeight: 600, color: '#0f172a' }}>
                    {partner.name}
                  </td>
                  
                  {/* Badge: Cliente (Azul) / Fornecedor (Roxo) */}
                  <td>
                    {partner.is_customer && partner.is_supplier ? (
                      <span className="badge badge-both">Misto</span>
                    ) : partner.is_customer ? (
                      <span className="badge badge-customer"><User size={12} className="mr-1"/> Cliente</span>
                    ) : (
                      <span className="badge badge-supplier"><Building2 size={12} className="mr-1"/> Fornecedor</span>
                    )}
                  </td>

                  {/* Documento Formatado */}
                  <td style={{ fontFamily: 'monospace', color: '#475569' }}>
                    {formatDocument(partner.document)}
                  </td>

                  {/* Localização */}
                  <td>
                    {partner.city ? (
                      <span className="flex items-center gap-1 text-slate-500 text-sm">
                        <MapPin size={14} /> {partner.city} - {partner.state}
                      </span>
                    ) : (
                      <span className="text-slate-400 text-xs">-</span>
                    )}
                  </td>

                  {/* Ações */}
                  <td style={{ textAlign: 'right' }}>
                    <button className="action-btn mr-2" title="Editar" onClick={() => { setEditingPartner(partner); setIsModalOpen(true); }}>
                      <Edit size={18} />
                    </button>
                    <button 
                      className="action-btn delete" 
                      title="Excluir"
                      onClick={(e) => handleDelete(e, partner.id)}
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        
        {/* 4. PAGINAÇÃO */}
        <div className="pagination-controls">
           <button 
             className="action-btn flex items-center gap-1 px-3 py-1 bg-white border border-slate-200" 
             disabled={page === 0} 
             onClick={() => setPage(p => Math.max(0, p - 1))}
           >
             Anterior
           </button>
           <span className="text-sm text-slate-500 self-center">Página {page + 1}</span>
           <button 
             className="action-btn flex items-center gap-1 px-3 py-1 bg-white border border-slate-200" 
             disabled={partners.length < LIMIT} 
             onClick={() => setPage(p => p + 1)}
           >
             Próximo <ArrowRight size={14} />
           </button>
        </div>
      </div>

      {/* MODAL DE CRIAÇÃO */}
      <CreatePartnerModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => {
          fetchPartners(); // Atualiza a tabela ao criar
        }}
        partnerToEdit={editingPartner || undefined}
      />

    </div>
  );
}