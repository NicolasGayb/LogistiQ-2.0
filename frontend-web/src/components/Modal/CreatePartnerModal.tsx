import { useState, useEffect, type FormEvent } from 'react';
import { X, Save, Loader2, User, MapPin, Building } from 'lucide-react';
import api from '../../api/client';
import './Modal.css';
import { useAuthContext } from '../../context/AuthContext';

interface Partner {
  id: string;
  name: string;
  document: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  is_customer: boolean;
  is_supplier: boolean;
  company_id?: string;
}

interface CreatePartnerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  partnerToEdit?: Partner; // Se for editar, recebe o parceiro existente
}

interface CompanyOption {
  id: string;
  name: string;
}

export function CreatePartnerModal({ isOpen, onClose, onSuccess, partnerToEdit }: CreatePartnerModalProps) {
    const { user } = useAuthContext();
  // --- ESTADOS ---
  
  // Controle de Tipo (PF/PJ) para máscara
  const [personType, setPersonType] = useState<'PF' | 'PJ'>('PJ');

  // Dados Principais
  const [name, setName] = useState('');
  const [document, setDocument] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  
  // Classificação
  const [isCustomer, setIsCustomer] = useState(true);
  const [isSupplier, setIsSupplier] = useState(false);

  // Endereço
  const [cep, setCep] = useState('');
  const [address, setAddress] = useState(''); // Rua
  const [number, setNumber] = useState('');
  const [neighborhood, setNeighborhood] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');

  // Lógica pra System Admin escolher empresa
  const [companies, setCompanies] = useState<CompanyOption[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');

  // UI
  const [loading, setLoading] = useState(false);
  const [loadingCep, setLoadingCep] = useState(false);

  // Reset ao abrir
  useEffect(() => {
    if (isOpen) {
        if (partnerToEdit) {
            // Modo de edição: Preenche com dados existentes
            setName(partnerToEdit.name);
            setDocument(partnerToEdit.document);
            setEmail(partnerToEdit.email || '');
            setPhone(partnerToEdit.phone || '');
            setAddress(partnerToEdit.address || '');
            setCity(partnerToEdit.city || '');
            setState(partnerToEdit.state || '');
            setIsCustomer(partnerToEdit.is_customer);
            setIsSupplier(partnerToEdit.is_supplier);

            const docLimpo = (partnerToEdit.document || '').replace(/\D/g, '');
            setPersonType(docLimpo.length === 11 ? 'PF' : 'PJ');

            setSelectedCompanyId(partnerToEdit.company_id || '');
        } else {
            // Modo criação: Limpa tudo
            setName(''); setDocument(''); setEmail(''); setPhone('');
            setCep(''); setAddress(''); setNumber(''); setNeighborhood(''); setCity(''); setState('');
            setIsCustomer(true); setIsSupplier(false);
            setPersonType('PJ');
            setSelectedCompanyId('');
        }

    // Se for System Admin, busca lista de empresas
    if (user?.role === 'SYSTEM_ADMIN') {
        fetchCompanies();
      }
    }
  }, [isOpen, user]);

  const fetchCompanies = async () => {
    try {
        const response = await api.get('/companies/list');
        if (Array.isArray(response.data)) {        
            setCompanies(response.data);
        } else {
            console.error("Resposta inesperada ao buscar empresas:", response.data);
            setCompanies([]);
        }
    } catch (error: any) {
        console.error("Erro ao buscar as empresas", error);
        alert(error.response?.data?.detail || "Erro ao buscar as empresas");
    }
};

  // --- MÁSCARAS E FORMATAÇÃO ---

  const handleDocumentChange = (val: string) => {
    // Remove tudo que não é número
    const numeric = val.replace(/\D/g, '');
    let masked = numeric;

    if (personType === 'PF') {
      // Máscara CPF: 000.000.000-00
      masked = numeric.replace(/(\d{3})(\d)/, '$1.$2')
                      .replace(/(\d{3})(\d)/, '$1.$2')
                      .replace(/(\d{3})(\d{1,2})/, '$1-$2')
                      .replace(/(-\d{2})\d+?$/, '$1');
    } else {
      // Máscara CNPJ: 00.000.000/0000-00
      masked = numeric.replace(/(\d{2})(\d)/, '$1.$2')
                      .replace(/(\d{3})(\d)/, '$1.$2')
                      .replace(/(\d{3})(\d)/, '$1/$2')
                      .replace(/(\d{4})(\d)/, '$1-$2')
                      .replace(/(-\d{2})\d+?$/, '$1');
    }
    setDocument(masked);
  };

  const handlePhoneChange = (val: string) => {
    const numeric = val.replace(/\D/g, '');
    // Máscara Telefone: (00) 00000-0000
    const masked = numeric.replace(/(\d{2})(\d)/, '($1) $2')
                          .replace(/(\d{5})(\d)/, '$1-$2')
                          .replace(/(-\d{4})\d+?$/, '$1');
    setPhone(masked);
  };

  const handleCepChange = (val: string) => {
    const numeric = val.replace(/\D/g, '');
    const masked = numeric.replace(/(\d{5})(\d)/, '$1-$2').substring(0, 9);
    setCep(masked);
  };

  // --- LÓGICA DE CEP (ViaCEP) ---
  const handleCepBlur = async () => {
    const cleanCep = cep.replace(/\D/g, '');
    if (cleanCep.length !== 8) return;

    setLoadingCep(true);
    try {
      // Busca direta na API pública do ViaCEP
      const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
      const data = await response.json();

      if (!data.erro) {
        setAddress(data.logradouro);
        setNeighborhood(data.bairro);
        setCity(data.localidade);
        setState(data.uf);
        // Foca no número automaticamente
        window.document.getElementById('addr-number')?.focus();
      } else {
        alert("CEP não encontrado.");
      }
    } catch (error) {
      console.error("Erro ao buscar CEP", error);
    } finally {
      setLoadingCep(false);
    }
  };

  // --- SUBMIT ---
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const cleanDoc = document.replace(/\D/g, '');

    if (!cleanDoc) {
      alert(`O campo ${personType === 'PJ' ? 'CNPJ' : 'CPF'} é obrigatório.`);
      return;
    }

    if (personType === 'PJ' && cleanDoc.length !== 14) {
       alert("CNPJ incompleto. Verifique os números.");
       return;
    }

    if (personType === 'PF' && cleanDoc.length !== 11) {
       alert("CPF incompleto. Verifique os números.");
       return;
    }

    if (user?.role === 'SYSTEM_ADMIN' && !selectedCompanyId) {
      alert("Por favor, selecione uma empresa para vincular este parceiro.");
      return;
    }

    if (!isCustomer && !isSupplier) {
      alert("Selecione: Cliente, Fornecedor ou ambos.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        company_id: selectedCompanyId || undefined, // Só envia se tiver selecionado (System Admin)
        name,
        document: document.replace(/\D/g, ''), // Envia limpo pro backend
        email: email || null,
        phone: phone || null,
        address: `${address}, ${number} - ${neighborhood}`, 
        city,
        state,
        is_customer: isCustomer,
        is_supplier: isSupplier,
        active: true
      };

      if (partnerToEdit) {
        await api.put(`/partners/${partnerToEdit.id}`, payload);
      } else {
        await api.post('/partners/', payload);
      }

      onSuccess();
      onClose();
    } catch (error: any) {
      const msg = error.response?.data?.detail || "Erro ao salvar parceiro.";
      alert(msg); // Backend valida duplicidade aqui
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '700px' }}>
        
        {/* HEADER */}
        <div className="modal-header">
          <h2 className="modal-title">{partnerToEdit ? "Editar Parceiro" : "Novo Parceiro"}</h2>
          <button className="close-button" onClick={onClose} type="button">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>

          {/* Se for System Admin, mostra dropdown de empresas */}
          {user?.role === 'SYSTEM_ADMIN' && (
            <div className="mb-6 bg-slate-50 p-4 rounded-lg border border-slate-200">
               <div className="form-section-title mt-0 text-orange-600 border-orange-200">
                <Building size={16} /> Seleção de Empresa (Admin)
              </div>
              <div className="form-group mt-2">
                <label className="form-label">Vincular à Empresa</label>
                <select 
                  className="form-select"
                  value={selectedCompanyId}
                  onChange={(e) => setSelectedCompanyId(e.target.value)}
                  required
                >
                  <option value="">Selecione uma empresa...</option>
                  {Array.isArray(companies) && companies.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
          
          {/* --- SEÇÃO 1: DADOS PRINCIPAIS --- */}
          <div className="form-section-title">
            <User size={16} /> Dados Cadastrais
          </div>

          {/* Tipo de Cadastro (Radio) */}
          <div className="form-group">
            <label className="form-label">Tipo de Pessoa</label>
            <div className="flex gap-4 mt-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="radio" 
                  name="personType"
                  checked={personType === 'PJ'}
                  onChange={() => { setPersonType('PJ'); setDocument(''); }}
                />
                <span className="text-sm font-medium text-slate-700">Pessoa Jurídica (CNPJ)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="radio" 
                  name="personType"
                  checked={personType === 'PF'}
                  onChange={() => { setPersonType('PF'); setDocument(''); }} 
                />
                <span className="text-sm font-medium text-slate-700">Pessoa Física (CPF)</span>
              </label>
            </div>
          </div>

          {/* Nome e Documento */}
          <div className="form-row" style={{ gridTemplateColumns: '1.5fr 1fr' }}>
            <div className="form-group">
              <label className="form-label">Nome / Razão Social <span className="text-red-500">*</span></label>
              <input 
                className="form-input" 
                value={name}
                onChange={e => setName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">{personType === 'PJ' ? 'CNPJ' : 'CPF'}</label>
              <input 
                className="form-input" 
                value={document}
                onChange={e => handleDocumentChange(e.target.value)}
                placeholder={personType === 'PJ' ? '00.000.000/0000-00' : '000.000.000-00'}
                maxLength={18}
                required
              />
            </div>
          </div>

          {/* Contato */}
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">E-mail</label>
              <input 
                type="email"
                className="form-input" 
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Telefone / Celular</label>
              <input 
                className="form-input" 
                value={phone}
                onChange={e => handlePhoneChange(e.target.value)}
              />
            </div>
          </div>

          {/* Classificação (Checkbox) */}
          <div className="form-group bg-slate-50 p-3 rounded-lg border border-slate-200">
            <label className="form-label mb-2">Classificação do Parceiro <span className="text-red-500">*</span></label>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={isCustomer}
                  onChange={e => setIsCustomer(e.target.checked)}
                  className="w-4 h-4 accent-emerald-600"
                />
                <span className="text-sm font-semibold text-blue-700">Cliente</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={isSupplier}
                  onChange={e => setIsSupplier(e.target.checked)}
                  className="w-4 h-4 accent-emerald-600"
                />
                <span className="text-sm font-semibold text-purple-700">Fornecedor</span>
              </label>
            </div>
          </div>

          {/* --- SEÇÃO 2: ENDEREÇO --- */}
          <div className="form-section-title mt-6">
            <MapPin size={16} /> Endereço Logístico
          </div>

          <div className="form-row" style={{ gridTemplateColumns: '150px 1fr' }}>
            <div className="form-group">
              <label className="form-label">CEP</label>
              <div className="relative">
                <input 
                  className="form-input" 
                  value={cep}
                  onChange={e => handleCepChange(e.target.value)}
                  onBlur={handleCepBlur}
                  placeholder="00000-000"
                  maxLength={9}
                />
                {loadingCep && (
                  <Loader2 size={16} className="absolute right-3 top-3 animate-spin text-emerald-600"/>
                )}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Endereço (Rua)</label>
              <input 
                className="form-input" 
                value={address}
                onChange={e => setAddress(e.target.value)}
                readOnly={loadingCep} // Trava enquanto busca
              />
            </div>
          </div>

          <div className="form-row" style={{ gridTemplateColumns: '100px 1fr 1fr' }}>
            <div className="form-group">
              <label className="form-label">Número</label>
              <input 
                id="addr-number"
                className="form-input" 
                value={number}
                onChange={e => setNumber(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Bairro</label>
              <input 
                className="form-input" 
                value={neighborhood}
                onChange={e => setNeighborhood(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Cidade / UF</label>
              <div className="flex gap-2">
                <input 
                  className="form-input flex-1" 
                  value={city}
                  onChange={e => setCity(e.target.value)}
                />
                <input 
                  className="form-input w-16 text-center" 
                  value={state}
                  onChange={e => setState(e.target.value)}
                  maxLength={2}
                />
              </div>
            </div>
          </div>

          {/* AÇÕES */}
          <div className="modal-actions">
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? (
                <> <Loader2 size={18} className="animate-spin mr-2" /> Salvando... </>
              ) : (
                <> <Save size={18} className="mr-2" /> {partnerToEdit ? 'Salvar Alterações' : 'Cadastrar Parceiro'} </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}