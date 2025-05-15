/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { createContext, PropsWithChildren, useMemo, useState } from "react";
import { scaleTime } from "@visx/scale";
import { useParentSize } from "@visx/responsive";
import {
  VisualizationContextProviderProps,
  VisualizationContextValue,
} from "./visualizationContext.types";

export const VisualizationContext = createContext<
  VisualizationContextValue | undefined
>(undefined);

export const VisualizationContextProvider = ({
  defaultMargin = { top: 50, right: 30, bottom: 25, left: 60 },
  children,
}: PropsWithChildren<VisualizationContextProviderProps>) => {
  const now = new Date();
  const todayNoon = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
    12
  );
  const previousNoon = new Date(todayNoon);
  previousNoon.setDate(previousNoon.getDate() - 1);

  const [zoomDomain, setZoomDomain] = useState<[Date, Date]>([
    previousNoon,
    todayNoon,
  ]);
  const [minRangeReached, setMinRangeReached] = useState(false);
  const [maxRangeReached, setMaxRangeReached] = useState(false);

  const { parentRef, width } = useParentSize();
  const height = 400;

  const xScale = useMemo(() => {
    return scaleTime({
      domain: zoomDomain,
      range: [defaultMargin.left, width - defaultMargin.right],
    });
  }, [zoomDomain, width, defaultMargin]);

  const xTicks = useMemo(() => {
    if (width >= 1200) {
      return 80;
    } else if (width >= 800) {
      return 60;
    }
    return 40;
  }, [width]);

  const onZoomChange = (domain: [number, number]) => {
    const [left, right] = domain;
    let range = right - left;

    // If the resulting range is less than or equal to 30 minutes
    if (range <= 1800000) {
      range = 1800000;
      setMinRangeReached(true);
    } else {
      setMinRangeReached(false);
    }
    setMaxRangeReached(false);

    setZoomDomain([new Date(domain[0]), new Date(domain[1])]);
  };

  const resetZoom = () => {
    setMinRangeReached(false);
    setMaxRangeReached(false);
    setZoomDomain([previousNoon, todayNoon]);
  };

  const panLeft = () => {
    const [left, right] = zoomDomain;
    const leftTimestamp = left.getTime();
    const rightTimestamp = right.getTime();
    const panAmount = (rightTimestamp - leftTimestamp) / 2;
    const newLeft = new Date(leftTimestamp - panAmount);
    const newRight = new Date(rightTimestamp - panAmount);
    setZoomDomain([newLeft, newRight]);
  };

  const panRight = () => {
    const [left, right] = zoomDomain;
    const leftTimestamp = left.getTime();
    const rightTimestamp = right.getTime();
    const panAmount = (rightTimestamp - leftTimestamp) / 2;
    const newLeft = new Date(leftTimestamp + panAmount);
    const newRight = new Date(rightTimestamp + panAmount);
    setZoomDomain([newLeft, newRight]);
  };

  const zoomIn = () => {
    const [left, right] = zoomDomain;
    const leftTimestamp = left.getTime();
    const rightTimestamp = right.getTime();
    let range = rightTimestamp - leftTimestamp;

    // If the resulting range is less than or equal to 30 minutes
    if (range <= 1800000) {
      range = 1800000;
      setMinRangeReached(true);
    } else {
      setMinRangeReached(false);
    }
    setMaxRangeReached(false);

    const newLeft = new Date(leftTimestamp + range / 4);
    const newRight = new Date(rightTimestamp - range / 4);
    setZoomDomain([newLeft, newRight]);
  };

  const zoomOut = () => {
    const [left, right] = zoomDomain;
    const leftTimestamp = left.getTime();
    const rightTimestamp = right.getTime();
    let range = rightTimestamp - leftTimestamp;

    // If the resulting range is greater than or equal to 7 days
    if (range >= 518400000) {
      range = 1800000;
      setMaxRangeReached(true);
    } else {
      setMaxRangeReached(false);
    }
    setMinRangeReached(false);

    const newLeft = new Date(leftTimestamp - range / 2);
    const newRight = new Date(rightTimestamp + range / 2);
    setZoomDomain([newLeft, newRight]);
  };

  return (
    <VisualizationContext.Provider
      value={{
        zoomDomain,
        minRangeReached,
        maxRangeReached,
        parentRef,
        width,
        height,
        defaultMargin,
        xScale,
        xTicks,
        onZoomChange,
        resetZoom,
        panLeft,
        panRight,
        zoomIn,
        zoomOut,
      }}
    >
      <div ref={parentRef} className="w-full">
        {children}
      </div>
    </VisualizationContext.Provider>
  );
};
