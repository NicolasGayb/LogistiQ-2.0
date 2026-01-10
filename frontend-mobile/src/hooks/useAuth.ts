import { useAuthContext } from "../context/AuthContext";

export function useAuth() {
  const context = useAuthContext();

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  const { user, isAuthenticated, loading, login, logout } = context;

  return {
    user,
    role: user?.role,
    companyId: user?.company_id,
    isAuthenticated,
    loading,
    login,
    logout,
  };
}