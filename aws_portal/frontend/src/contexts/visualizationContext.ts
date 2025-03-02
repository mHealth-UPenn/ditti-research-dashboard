import { ScaleTime } from "d3";
import { createContext, RefObject, useContext } from "react";

interface IVisualizationContext {
  zoomDomain: [Date, Date] | null;  // Ensure different types can be added in the future by enforcing type checks now
  minRangeReached: boolean;
  maxRangeReached: boolean;
  parentRef: RefObject<HTMLDivElement>;
  width: number;
  height: number;
  defaultMargin: { top: number; right: number; bottom: number; left: number };
  xScale: ScaleTime<number, number> | null;
  xTicks: number;
  onZoomChange: (domain: [number, number]) => void;
  resetZoom: () => void;
  panLeft: () => void;
  panRight: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
}

export const VisualizationContext = createContext<IVisualizationContext | undefined>(undefined);


export const useVisualizationContext = () => {
  const context = useContext(VisualizationContext);
  if (!context) {
    throw new Error("useVisualizationContext must be used within a VisualizationContext provider");
  }
  return context;
};
