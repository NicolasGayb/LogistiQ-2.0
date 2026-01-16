export type UserRole = 'SYSTEM_ADMIN' | 'ADMIN' | 'MANAGER' | 'USER'

export interface UserMe{
    id: string,
    name: string,
    email: string,
    role: UserRole,
    company_id: string | null,
    company_name: string | null,
    is_active: boolean;
}

export interface LoginResponse{
    access_token: string,
    token_type: 'bearer'
}