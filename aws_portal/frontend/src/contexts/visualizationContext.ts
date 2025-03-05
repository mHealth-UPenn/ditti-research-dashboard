/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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


export default VisualizationContext;
