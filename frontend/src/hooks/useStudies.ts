import { useContext } from "react";
import { StudiesContext } from "../contexts/studiesContext";

// Hook for accessing context data
export function useStudies() {
  const context = useContext(StudiesContext);
  if (!context) {
    throw new Error("useStudies must be used within a StudiesContext provider");
  }
  return context;
}
