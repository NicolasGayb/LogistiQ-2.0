import { useMovementsContext } from "../context/MovementsContext";

export function useMovements() {
  return useMovementsContext();
}
