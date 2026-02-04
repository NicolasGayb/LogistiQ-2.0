import api from '../api/client';

export interface Product {
  id: string;
  name: string;
  description?: string;
  sku: string;
  price: number;
  quantity: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  updated_by?: string; // ID do usuário que fez a última modificação
  updated_by_name?: string;
  company_name?: string;
}

export const ProductService = {
  getAll: async () => {
    const response = await api.get<Product[]>('/products/');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<Product>(`/products/${id}`);
    return response.data;
  },

  create: async (data: Omit<Product, 'id' | 'is_active'>) => {
    const response = await api.post<Product>('/products/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Product>) => {
    const response = await api.put<Product>(`/products/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/products/${id}`);
  },

  toggleActive: async (id: string) => {
    const response = await api.patch<Product>(`/products/${id}/toggle`);
    return response.data;
  }
};