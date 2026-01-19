export const ROLE_HIERARCHY = {
  SYSTEM_ADMIN: 4,
  ADMIN: 3,
  MANAGER: 2,
  USER: 1,
} as const;

export type UserRole = keyof typeof ROLE_HIERARCHY;
