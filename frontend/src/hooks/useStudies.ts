import { useContext } from "react";
import { StudiesContext } from "../contexts/studiesContext";
import { StudiesContextValue } from "../contexts/studiesContext.types";

/**
 * Hook for accessing context data
 * @returns The current studies context.
 */
export function useStudies(): StudiesContextValue {
  const context = useContext(StudiesContext);
  if (!context) {
    throw new Error("useStudies must be used within a StudiesContext provider");
  }
  return context;
}
