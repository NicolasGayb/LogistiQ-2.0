export type UserRole = 'SYSTEM_ADMIN' | 'ADMIN' | 'USER';

export interface UserMe {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  company_id: number | null;
  company_name: string | null;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
}
