import { useProductsContext } from "../context/ProductsContext";
import { useAuth } from "./useAuth";

export function useProducts() {
  const productsContext = useProductsContext();
  const { role } = useAuth();

  if (!productsContext) {
    throw new Error("useProducts must be used inside ProductsProvider");
  }

  const {
    products,
    selectedProduct,
    loading,
    fetchProducts,
    fetchProductById,
    createProduct,
    updateProduct,
  } = productsContext;

  const canManageProducts = role === "ADMIN";

  return {
    products,
    selectedProduct,
    loading,
    fetchProducts,
    fetchProductById,

    // só ADMIN recebe essas funções
    createProduct: canManageProducts ? createProduct : undefined,
    updateProduct: canManageProducts ? updateProduct : undefined,
  };
}