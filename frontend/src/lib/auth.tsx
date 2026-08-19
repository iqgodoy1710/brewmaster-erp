import {
  createContext,
  useContext,
} from "react";
import type { ReactNode } from "react";

import { isAuthRequired } from "./api";
import type {
  AuthenticatedUser,
  UserRole,
} from "../types/api";

const AuthContext = createContext<AuthenticatedUser | null>(
  null,
);

type AuthProviderProps = {
  children: ReactNode;
  user: AuthenticatedUser | null;
};

export function AuthProvider({
  children,
  user,
}: AuthProviderProps) {
  return (
    <AuthContext.Provider value={user}>
      {children}
    </AuthContext.Provider>
  );
}

export function useCurrentUser() {
  return useContext(AuthContext);
}

export function hasRole(
  user: AuthenticatedUser | null,
  ...roles: UserRole[]
): boolean {
  if (!isAuthRequired) {
    return true;
  }

  return user !== null && roles.includes(user.role);
}