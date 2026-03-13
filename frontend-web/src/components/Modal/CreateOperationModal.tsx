import { useState, useEffect } from 'react';
import { X, ArrowRight, ArrowLeft, Plus, Trash2, Package } from 'lucide-react';
import api from '../../api/client';
import { useAuthContext } from '../../context/AuthContext';
import './Modal.css';

// --- INTERFACES ---
interface Product {
  id: string;
  name: string;
  sku: string;
  current_stock: number;
  price: number;
}

interface Partner {
  id: string;
  name: string;
}

interface CartItem {
  productId: string;
  productName: string;
  productSku: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
}

interface CreateOperationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreateOperationModal({ isOpen, onClose, onSuccess }: CreateOperationModalProps) {
  const { user } = useAuthContext(); // <--- PEGAR O USUÁRIO LOGADO

  // --- ESTADOS DO WIZARD ---
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Dados Gerais
  const [referenceCode, setReferenceCode] = useState('');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');

  // Estado para exibir o nome da empresa do usuário logado
  const [myCompanyName, setMyCompanyName] = useState('');

  // Dados Step 1 (Cabeçalho)
  const [type, setType] = useState<'PICKUP' | 'DELIVERY'>('PICKUP');
  const [partnerId, setPartnerId] = useState('');
  const [date, setDate] = useState('');

  // Dados Step 2 (Itens)
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState<number>(1);
  
  // Dados Step 3 (Final)
  const [observation, setObservation] = useState('');

  // Listas da API
  const [partners, setPartners] = useState<Partner[]>([]);
  const [products, setProducts] = useState<Product[]>([]);

  // --- RESET E LOAD INICIAL ---
  useEffect(() => {
    if (isOpen) {
      // Resetar todos os estados
      setStep(1);
      setReferenceCode('');
      setOrigin('');
      setDestination('');
      setType('PICKUP');
      setPartnerId('');
      setDate('');
      setCart([]);
      setSelectedProductId('');
      setQuantity(1);
      setObservation('');

      // Carregar dados iniciais
      fetchInitialData();
    }
  }, [isOpen]);

  // --- PREENCHIMENTO AUTOMÁTICO DINÂMICO ---
  useEffect(() => {
    if (!isOpen) return;
      
    const selectedPartner = partners.find(p => p.id === partnerId);
    const partnerName = selectedPartner ? selectedPartner.name : 'Parceiro';

    const companyText = myCompanyName ? `${myCompanyName} (Minha Empresa)` : 'Minha Empresa';

    if (type === 'PICKUP') {
      // Entrada (PICKUP): Origem = Parceiro, Destino = Minha Empresa
      if (partnerName) setOrigin(partnerName);
      setDestination(companyText);
    } else {
      // Saída (DELIVERY): Origem = Minha Empresa, Destino = Parceiro
      setOrigin(companyText);
      if (partnerName) setDestination(partnerName);
    }
  }, [type, partnerId, partners, isOpen, myCompanyName]);

  const fetchInitialData = async () => {
    try {
      const [resPartners, resProducts, resCompanies] = await Promise.all([
        api.get('/partners/'),
        api.get('/products/'),
        api.get('/companies/me') // Endpoint para obter a empresa do usuário logado
      ]);
      
      if (Array.isArray(resPartners.data)) setPartners(resPartners.data);
      if (Array.isArray(resProducts.data)) setProducts(resProducts.data);

      if (resCompanies.data && resCompanies.data.name) {
        setMyCompanyName(resCompanies.data.name);
      }
    } catch (error) {
      console.error("Erro ao carregar dados", error);
    }
  };

  // --- LÓGICA DO CARRINHO ---
  const handleAddItem = () => {
    if (!selectedProductId || quantity <= 0) return;

    const product = products.find(p => p.id === selectedProductId);
    if (!product) return;

    // REGRA DE NEGÓCIO: Validação de Estoque na Saída
    if (type === 'DELIVERY') {
      const currentInCart = cart.find(item => item.productId === product.id)?.quantity || 0;
      const totalRequested = quantity + currentInCart;

      if (totalRequested > product.current_stock) {
        alert(`Estoque insuficiente! Disponível: ${product.current_stock}, Solicitado: ${totalRequested}`);
        return;
      }
    }

    // Adiciona ou Atualiza no Carrinho
    setCart(prev => {
      const existingIndex = prev.findIndex(item => item.productId === product.id);
      if (existingIndex >= 0) {
        const newCart = [...prev];
        newCart[existingIndex].quantity += quantity;
        newCart[existingIndex].subtotal = newCart[existingIndex].quantity * product.price;
        return newCart;
      } else {
        return [...prev, {
          productId: product.id,
          productName: product.name,
          productSku: product.sku,
          quantity: quantity,
          unitPrice: product.price,
          subtotal: quantity * product.price
        }];
      }
    });

    // Limpa inputs parciais
    setSelectedProductId('');
    setQuantity(1);
  };

  const handleRemoveItem = (prodId: string) => {
    setCart(prev => prev.filter(item => item.productId !== prodId));
  };

  const cartTotal = cart.reduce((acc, item) => acc + item.subtotal, 0);

  // --- SUBMIT FINAL ---
  const handleFinalSubmit = async () => {
    if (cart.length === 0) {
      alert("Adicione pelo menos um item à operação.");
      return;
    }
    
    // Validação final de segurança
    if (!referenceCode || !origin || !destination) {
      alert("Preencha os dados obrigatórios no Passo 1 (Referência, Origem e Destino).");
      setStep(1); 
      return;
    }

    setLoading(true);
    try {
      const payload = {
        reference_code: referenceCode,
        origin: origin,
        destination: destination,
        type,
        partner_id: partnerId,
        expected_date: date || null,
        observation: observation || null,
        items: cart.map(item => ({
          product_id: item.productId,
          quantity: item.quantity,
          unit_price: item.unitPrice
        }))
      };

      await api.post('/operations/', payload);
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error(error);
      const msg = error.response?.data?.detail || "Erro ao criar operação.";
      alert(typeof msg === 'object' ? JSON.stringify(msg) : msg);
    } finally {
      setLoading(false);
    }
  };

  // --- VALIDAÇÃO DE NAVEGAÇÃO ---
  const handleNextStep = () => {
    if (step === 1) {
      if (!partnerId) return alert('Selecione um parceiro.');
      if (!referenceCode) return alert('O Código de Referência é obrigatório.');
      if (!origin) return alert('A Origem é obrigatória.');
      if (!destination) return alert('O Destino é obrigatório.');
    }
    setStep(s => s + 1);
  };

  // --- RENDERIZADORES DOS PASSOS ---

  // Passo 1: Cabeçalho
  const renderStep1 = () => (
    <div className="animate-fadeIn space-y-4">
      
      {/* Tipo de Operação */}
      <div className="form-group">
        <label className="form-label">Tipo de Operação</label>
        <div className="flex gap-4 mt-1">
          <label className={`flex items-center gap-2 cursor-pointer p-3 border rounded-lg w-full justify-center transition-all ${type === 'PICKUP' ? 'bg-emerald-50 border-emerald-500 text-emerald-700' : 'bg-white border-slate-200'}`}>
            <input type="radio" name="opType" checked={type === 'PICKUP'} onChange={() => { setType('PICKUP'); setCart([]); }} className="hidden" />
            <ArrowRight size={18} /> Entrada
          </label>
          <label className={`flex items-center gap-2 cursor-pointer p-3 border rounded-lg w-full justify-center transition-all ${type === 'DELIVERY' ? 'bg-purple-50 border-purple-500 text-purple-700' : 'bg-white border-slate-200'}`}>
            <input type="radio" name="opType" checked={type === 'DELIVERY'} onChange={() => { setType('DELIVERY'); setCart([]); }} className="hidden" />
            <ArrowLeft size={18} /> Saída
          </label>
        </div>
      </div>

      {/* Código de Referência */}
      <div className="form-group">
        <label className="form-label">Código de Referência <span className="text-red-500">*</span></label>
        <input 
          className="form-input"
          value={referenceCode}
          onChange={e => setReferenceCode(e.target.value)}
          placeholder="Ex: PO-2026-001 ou NF 1234"
        />
      </div>

      {/* Parceiro e Data */}
      <div className="form-row">
        <div className="form-group flex-1">
          <label className="form-label">Parceiro de Negócio <span className="text-red-500">*</span></label>
          <select 
            className="form-select"
            value={partnerId}
            onChange={e => setPartnerId(e.target.value)}
          >
            <option value="">Selecione...</option>
            {partners.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
        <div className="form-group w-40">
          <label className="form-label">Data Prevista</label>
          <input 
            type="date" 
            className="form-input"
            value={date}
            onChange={e => setDate(e.target.value)}
          />
        </div>
      </div>

      {/* Origem e Destino */}
      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Origem <span className="text-red-500">*</span></label>
          <input 
            className="form-input"
            value={origin}
            onChange={e => setOrigin(e.target.value)}
            placeholder="Local de Saída"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Destino <span className="text-red-500">*</span></label>
          <input 
            className="form-input"
            value={destination}
            onChange={e => setDestination(e.target.value)}
            placeholder="Local de Entrega"
          />
        </div>
      </div>
    </div>
  );

  // Passo 2: Itens
  const renderStep2 = () => {
    return (
      <div className="animate-fadeIn">
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-4 flex gap-3 items-end">
          <div className="flex-1">
            <label className="form-label text-xs mb-1">Produto</label>
            <select 
              className="form-select text-sm"
              value={selectedProductId}
              onChange={e => setSelectedProductId(e.target.value)}
            >
              <option value="">Selecione um produto...</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>
                   {p.sku} - {p.name} ({type === 'DELIVERY' ? `Estoque: ${p.current_stock}` : 'Livre'})
                </option>
              ))}
            </select>
          </div>
          
          <div className="w-24">
            <label className="form-label text-xs mb-1">Qtd.</label>
            <input 
              type="number" 
              min="1"
              className="form-input text-sm"
              value={quantity}
              onChange={e => setQuantity(Number(e.target.value))}
            />
          </div>

          <button 
            type="button" 
            onClick={handleAddItem}
            className="h-[42px] px-4 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors flex items-center justify-center"
            title="Adicionar item"
          >
            <Plus size={20} />
          </button>
        </div>

        <div className="max-h-60 overflow-y-auto border rounded-lg bg-white">
          <table className="items-table">
            <thead>
              <tr>
                <th>Produto</th>
                <th className="text-center">Qtd</th>
                <th className="text-right">Total</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {cart.length === 0 ? (
                <tr><td colSpan={4} className="text-center py-6 text-slate-400">Nenhum item adicionado.</td></tr>
              ) : (
                cart.map(item => (
                  <tr key={item.productId}>
                    <td>
                      <div className="font-medium text-slate-700">{item.productName}</div>
                      <div className="text-xs text-slate-500">{item.productSku}</div>
                    </td>
                    <td className="text-center">{item.quantity}</td>
                    <td className="text-right">R$ {item.subtotal.toFixed(2)}</td>
                    <td className="text-right">
                      <button onClick={() => handleRemoveItem(item.productId)} className="remove-item-btn">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        <div className="flex justify-end mt-4 text-lg font-bold text-slate-800">
          Total Estimado: R$ {cartTotal.toFixed(2)}
        </div>
      </div>
    );
  };

  // Passo 3: Revisão
  const renderStep3 = () => (
    <div className="animate-fadeIn">
      <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-6 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-500">Ref:</span>
          <span className="font-bold text-slate-800">{referenceCode}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Tipo:</span>
          <span className="font-bold">{type === 'PICKUP' ? 'Entrada' : 'Saída'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Parceiro:</span>
          <span className="font-medium">{partners.find(p => p.id === partnerId)?.name || '-'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Origem:</span>
          <span className="font-medium">{origin}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Destino:</span>
          <span className="font-medium">{destination}</span>
        </div>
        <div className="flex justify-between pt-2 border-t border-slate-200 mt-2">
          <span className="text-slate-500">Total de Itens:</span>
          <span className="font-bold">{cart.length} produtos (R$ {cartTotal.toFixed(2)})</span>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Observações (Opcional)</label>
        <textarea 
          className="form-input" 
          rows={3}
          value={observation}
          onChange={e => setObservation(e.target.value)}
          placeholder="Ex: Nota fiscal nº 1234, entregar na doca 2..."
        />
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '800px' }}>
        
        <div className="modal-header">
          <h2 className="modal-title">Nova Operação</h2>
          <button className="close-button" onClick={onClose}><X size={20} /></button>
        </div>

        <div className="wizard-steps">
          <div className={`step-item ${step >= 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}>
            <div className="step-circle">1</div>
            <span className="step-label">Dados</span>
          </div>
          <div className={`step-item ${step >= 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}>
            <div className="step-circle">2</div>
            <span className="step-label">Itens</span>
          </div>
          <div className={`step-item ${step >= 3 ? 'active' : ''}`}>
            <div className="step-circle">3</div>
            <span className="step-label">Revisão</span>
          </div>
        </div>

        <div className="px-6 py-2 min-h-[350px]">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>

        <div className="modal-actions mt-4 pt-4 border-t border-slate-100 px-6 pb-6">
          
          {step > 1 ? (
            <button className="btn-secondary" onClick={() => setStep(s => s - 1)}>
              Voltar
            </button>
          ) : (
            <button className="btn-secondary" onClick={onClose}>
              Cancelar
            </button>
          )}

          {step < 3 ? (
            <button 
              className="btn-primary" 
              onClick={handleNextStep}
            >
              Próximo <ArrowRight size={18} className="ml-2"/>
            </button>
          ) : (
            <button className="btn-primary bg-emerald-600 hover:bg-emerald-700" onClick={handleFinalSubmit} disabled={loading}>
              {loading ? 'Salvando...' : 'Confirmar Operação'} <Package size={18} className="ml-2"/>
            </button>
          )}

        </div>

      </div>
    </div>
  );
}