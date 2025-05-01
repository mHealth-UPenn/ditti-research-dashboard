import { useContext } from "react";
import { NavbarContext } from "../contexts/navbarContext";
import { NavbarContextValue } from "../contexts/navbarContext.types";

/**
 * Hook for accessing context data
 * @returns The current navbar context.
 */
export function useNavbar(): NavbarContextValue {
  const context = useContext(NavbarContext);
  if (!context) {
    throw new Error("useNavbar must be used within a NavbarContext provider");
  }
  return context;
}
