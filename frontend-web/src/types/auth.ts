export type UserRole =
  | 'SYSTEM_ADMIN'
  | 'ADMIN'
  | 'MANAGER'
  | 'USER';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  companyId: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export const __auth_test__ = true;