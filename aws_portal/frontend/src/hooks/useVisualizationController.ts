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

import { useMemo, useState } from "react";
import { scaleTime } from '@visx/scale';
import { useParentSize } from '@visx/responsive'


// TODO: extend to customize default values when needed in future vizualizations
const useVisualizationController = (
  defaultMargin: { top: number, right: number, bottom: number, left: number }
) => {
  const now = new Date();
  const todayNoon = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  const previousNoon = new Date(todayNoon);
  previousNoon.setDate(previousNoon.getDate() - 1);

  const [zoomDomain, setZoomDomain] = useState<[Date, Date]>([previousNoon, todayNoon]);
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
  }, [width])

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
    setZoomDomain([previousNoon, todayNoon])
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

  return {
    zoomDomain,
    minRangeReached,
    maxRangeReached,
    parentRef,
    width,
    height,
    xScale,
    xTicks,
    onZoomChange,
    resetZoom,
    panLeft,
    panRight,
    zoomIn,
    zoomOut,
  };
};


export default useVisualizationController;
