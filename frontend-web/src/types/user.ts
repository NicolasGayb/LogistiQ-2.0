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