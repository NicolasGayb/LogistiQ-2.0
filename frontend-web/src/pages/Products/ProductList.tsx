import { useEffect, useState } from 'react';
import { Plus, Search, Edit2, AlertCircle, Package, XCircle, CheckCircle } from 'lucide-react';
import { ProductService, type Product } from '../../services/productService';
import CreateProductModal, { type ProductFormData } from '../../components/Modal/CreateProductModal';
import './ProductList.css';

export default function ProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // Estados para controle do Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  const fetchProducts = async () => {
    try {
      const data = await ProductService.getAll();
      setProducts(data);
    } catch (error) {
      console.error('Erro ao buscar produtos', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // --- LÓGICA DE ABRIR O MODAL ---
  
  // 1. Abrir para CRIAR
  const handleOpenCreate = () => {
    setEditingProduct(null); 
    setIsModalOpen(true);
  };

  // 2. Abrir para EDITAR
  const handleOpenEdit = (product: Product) => {
    setEditingProduct(product);
    setIsModalOpen(true);
  };

  // 3. Salvar (Serve para os dois casos)
  const handleSaveProduct = async (formData: ProductFormData) => {
    if (editingProduct) {
      // É Edição
      await ProductService.update(editingProduct.id, formData);
    } else {
      // É Criação
      await ProductService.create(formData);
    }
    await fetchProducts(); // Recarrega a tabela
  };

  // Filtra produtos com base no termo de busca
  const filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleToggleStatus = async (product: Product) => {
    const action = product.is_active ? 'desativar' : 'ativar';
    if (window.confirm(`Deseja realmente ${action} o produto "${product.name}"?`)) {
      try {
        await ProductService.toggleActive(product.id);
        await fetchProducts(); 
      } catch (error) {
        alert('Erro ao alterar status do produto.');
        console.error(error);
      }
    }
  };

  return (
    <div className="product-list-container">
        {/* HEADER E BOTÃO NOVO PRODUTO */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Estoque de Produtos</h1>
          <p className="page-subtitle">Gerencie seu catálogo e quantidades.</p>
        </div>
        <button onClick={handleOpenCreate} className="btn-add">
          <Plus size={20} />
          Novo Produto
        </button>
      </div>

        {/* BARRA DE BUSCA */}
      <div className="search-bar-container">
        <div className="search-input-wrapper">
          <Search className="search-icon" size={20} />
          <input 
            type="text"
            placeholder="Buscar por nome ou SKU..."
            className="search-input"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* TABELA DE PRODUTOS */}
      <div className="table-container">
        <table className="product-table">
          <thead>
            <tr>
              <th>Produto</th>
              <th>Empresa</th>
              <th>SKU</th>
              <th>Preço</th>
              <th>Estoque</th>
              <th>Status</th>
              <th>Modificado em/por</th>
              <th className="text-right">Ações</th>
            </tr>
          </thead>
          {/* CORPO DA TABELA */}
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="table-empty">Carregando estoque...</td></tr>
            ) : filteredProducts.length === 0 ? (
              <tr>
                <td colSpan={8} className="table-empty">
                  <div className="empty-state">
                    <Package size={48} />
                    <p>Nenhum produto encontrado.</p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredProducts.map(product => {
                const isLowStock = product.quantity <= 10;
                return (
                  <tr key={product.id}>
                    <td className="font-bold">{product.name}</td>
                    <td className="font-mono">{product.company_name}</td>
                    <td className="font-mono">{product.sku}</td>
                    <td>R$ {Number(product.price).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                    <td>
                      <div className={`stock-badge ${isLowStock ? 'low-stock' : 'normal-stock'}`}>
                        {product.quantity}
                        {isLowStock && <AlertCircle size={16} />}
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge ${product.is_active ? 'active' : 'inactive'}`}>
                        {product.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td>
                      <div className='cell-vertical'>
                        {/* Data e Hora da última modificação */}
                        <span className='text-date'>
                        {product.updated_at
                            ? new Date(product.updated_at).toLocaleString('pt-BR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit'
                              })
                            : 'N/A'}
                        </span>
                        {/* Nome do usuário que fez a última modificação */}
                        {(product.updated_by_name || product.updated_by) && (
                            <span className='text-user'>
                                {product.updated_by_name || product.updated_by}
                            </span>
                        )}
                      </div>
                    </td>
                    <td className="text-right">
                      <div className="action-buttons">
                        {/* Botões de Editar e Desativar/ativar */}
                        <button 
                          onClick={() => handleOpenEdit(product)}
                          className="btn-icon edit"
                          title="Editar"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                            onClick={() => handleToggleStatus(product)}
                            className={`btn-icon ${product.is_active ? 'deactivate' : 'activate'}`}
                            title={product.is_active ? 'Desativar' : 'Ativar'}
                        >
                          {product.is_active ? <XCircle size={18} /> : <CheckCircle size={18} />}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL */}
      <CreateProductModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveProduct}
        initialData={editingProduct ? {
            name: editingProduct.name,
            sku: editingProduct.sku,
            price: Number(editingProduct.price),
            quantity: Number(editingProduct.quantity),
            description: editingProduct.description || ''
        } : null}
      />
    </div>
  );
}