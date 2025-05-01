import { useContext } from "react";
import { AuthContext } from "../contexts/authContext";
import { AuthContextValue } from "../contexts/authContext.types";

/**
 * Custom hook to access authentication context.
 * Throws an error if used outside of an AuthProvider.
 * @returns The current authentication context.
 */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};
