import { useContext } from "react";
import { VisualizationContext } from "../contexts/visualizationContext";
import { VisualizationContextValue } from "../contexts/visualizationContext.types";

/**
 * Hook for retrieving context data
 * @returns The current visualization context.
 */
export const useVisualization = (): VisualizationContextValue => {
  const context = useContext(VisualizationContext);
  if (!context) {
    throw new Error(
      "useVisualization must be used within a VisualizationContext provider"
    );
  }
  return context;
};
