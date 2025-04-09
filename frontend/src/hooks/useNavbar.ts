import { useContext } from "react";
import { NavbarContext } from "../contexts/navbarContext";

// Hook for accessing context data
export function useNavbar() {
  const context = useContext(NavbarContext);
  if (!context) {
    throw new Error("useNavbar must be used within a NavbarContext provider");
  }
  return context;
}
