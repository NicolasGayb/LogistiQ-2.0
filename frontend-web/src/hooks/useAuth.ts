import { useAuthContext } from "../context/AuthContext";

export function useAuth() {
    const context = useAuthContext();

    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }

    const { user, isAuthenticated, loading, login, logout } = context;

    return {
        user,
        role: user?.role || null,
        companyId: user?.companyId || null,
        isAuthenticated,
        loading,
        login,
        logout,
    };
}