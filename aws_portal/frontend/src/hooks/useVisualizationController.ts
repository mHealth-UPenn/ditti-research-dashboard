import { useEffect, useMemo, useState } from "react";
import { scaleTime } from '@visx/scale';


const getWidthFromScreenSize = () => {
  if (window.innerWidth > 1600) {
    return 1200;
  } else if (window.innerWidth > 1400) {
    return 1000;
  } else if (window.innerWidth > 1000) {
    return 800;
  }
  return 600;
}


const useResponsiveWidth = () => {
  const [responsiveWidth, setReactiveWidth] = useState(getWidthFromScreenSize());

  useEffect(() => {
      window.addEventListener("resize", () => {
          setReactiveWidth(getWidthFromScreenSize());
      });
      return () => {
          window.removeEventListener("resize", () => {
              setReactiveWidth(getWidthFromScreenSize());
          })
      }
  }, []);

  return responsiveWidth;
}


const getTicksFromWidth = (width: number) => {
  if (width >= 1000) {
    return 50;
  } else if (width >= 800) {
    return 40;
  }
  return 20;
}


const useVisualizationController = () => {
  const now = new Date();
  const todayNoon = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  const previousNoon = new Date(todayNoon);
  previousNoon.setDate(previousNoon.getDate() - 1);

  const [zoomDomain, setZoomDomain] = useState<[Date, Date]>([previousNoon, todayNoon]);
  const [minRangeReached, setMinRangeReached] = useState(false);
  const [maxRangeReached, setMaxRangeReached] = useState(false);

  const width = useResponsiveWidth();
  const height = 400;
  const margin = { top: 20, right: 30, bottom: 50, left: 60 };

  const xScale = useMemo(() => {
    return scaleTime({
      domain: zoomDomain,
      range: [margin.left, width - margin.right],
    });
  }, [zoomDomain, width]);

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

  const resetZoom = () => setZoomDomain([previousNoon, todayNoon]);

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
    width,
    height,
    margin,
    xScale,
    onZoomChange,
    resetZoom,
    panLeft,
    panRight,
    zoomIn,
    zoomOut,
  };
};


export default useVisualizationController;
