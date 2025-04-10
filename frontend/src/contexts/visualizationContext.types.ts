import { ScaleTime } from "d3";
import { RefObject } from "react";

/**
 * Defines the context containing information about a visualization.
 * @property zoomDomain - The domain of the zoom.
 * @property minRangeReached - Whether the minimum range has been reached.
 * @property maxRangeReached - Whether the maximum range has been reached.
 * @property parentRef - The ref object of the parent element.
 * @property width - The width of the visualization.
 * @property height - The height of the visualization.
 * @property defaultMargin - The default margin of the visualization.
 * @property xScale - The x scale of the visualization.
 * @property xTicks - The x ticks of the visualization.
 * @property onZoomChange - The function to call when the zoom changes.
 * @property resetZoom - The function to call to reset the zoom.
 * @property panLeft - The function to call to pan left.
 * @property panRight - The function to call to pan right.
 * @property zoomIn - The function to call to zoom in.
 * @property zoomOut - The function to call to zoom out.
 */
export interface VisualizationContextValue {
  zoomDomain: [Date, Date] | null;
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

/**
 * Props for the VisualizationContextProvider component.
 * @property defaultMargin - The default margin of the visualization.
 */
export interface VisualizationContextProviderProps {
  defaultMargin?: { top: number, right: number, bottom: number, left: number };
}
