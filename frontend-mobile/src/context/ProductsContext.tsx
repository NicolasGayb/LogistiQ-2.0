import React, { createContext, useContext, useState } from "react";
import api from "../api/client";

export type Product = {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  min_quantity: number;
  created_at: string;
};

type ProductsContextData = {
  products: Product[];
  selectedProduct: Product | null;
  loading: boolean;
  fetchProducts: () => Promise<void>;
  fetchProductById: (id: string) => Promise<void>;
  createProduct: (data: Partial<Product>) => Promise<void>;
  updateProduct: (id: string, data: Partial<Product>) => Promise<void>;
};

const ProductsContext = createContext<ProductsContextData>(
  {} as ProductsContextData
);

export const ProductsProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(false);

  async function fetchProducts() {
    setLoading(true);
    try {
      const response = await api.get("/products");
      setProducts(response.data);
    } finally {
      setLoading(false);
    }
  }

  async function fetchProductById(id: string) {
    setLoading(true);
    try {
      const response = await api.get(`/products/${id}`);
      setSelectedProduct(response.data);
    } finally {
      setLoading(false);
    }
  }

  async function createProduct(data: Partial<Product>) {
    setLoading(true);
    try {
      await api.post("/products", data);
      await fetchProducts();
    } finally {
      setLoading(false);
    }
  }

  async function updateProduct(id: string, data: Partial<Product>) {
    setLoading(true);
    try {
      await api.put(`/products/${id}`, data);
      await fetchProducts();
    } finally {
      setLoading(false);
    }
  }

  return (
    <ProductsContext.Provider
      value={{
        products,
        selectedProduct,
        loading,
        fetchProducts,
        fetchProductById,
        createProduct,
        updateProduct,
      }}
    >
      {children}
    </ProductsContext.Provider>
  );
};

export function useProductsContext() {
  return useContext(ProductsContext);
}