import { useContext } from "react";
import { AuthContext } from "../AuthContext";
import { AuthContextType } from "../interfaces";

/**
 * Custom hook to access authentication context.
 * Throws an error if used outside of an AuthProvider.
 * @returns The current authentication context.
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};
