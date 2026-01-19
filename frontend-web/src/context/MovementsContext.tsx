import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";
import { endpoints } from "../api/endpoints";

export interface Movement {
  id: number;
  product_id: number;
  type: "IN" | "OUT";
  quantity: number;
  created_at: string;
}

interface MovementsContextData {
  movements: Movement[];
  isLoading: boolean;
  fetchMovements: () => Promise<void>;
}

const MovementsContext = createContext<MovementsContextData | undefined>(
  undefined
);

export function MovementsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  async function fetchMovements() {
    try {
      setIsLoading(true);
      const response = await api.get(endpoints.movements);
      setMovements(response.data);
    } catch (error) {
      console.error("Erro ao buscar movimentações:", error);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchMovements();
  }, []);

  return (
    <MovementsContext.Provider
      value={{
        movements,
        isLoading,
        fetchMovements,
      }}
    >
      {children}
    </MovementsContext.Provider>
  );
}

export function useMovementsContext() {
  const context = useContext(MovementsContext);

  if (!context) {
    throw new Error(
      "useMovementsContext deve ser usado dentro de MovementsProvider"
    );
  }

  return context;
}