import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { scaleTime, scaleLinear } from '@visx/scale';
import { Bar } from '@visx/shape';
import { Brush } from '@visx/brush';
import { AxisLeft, AxisBottom } from '@visx/axis';
import { bin as d3Histogram } from 'd3-array';
import { Bounds } from '@visx/brush/lib/types';
import { GridRows, GridColumns } from '@visx/grid';
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip"
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import ReplayIcon from '@mui/icons-material/Replay';

interface HistogramProps {
  timestamps: number[];
}


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
  console.log(width);
  if (width >= 1000) {
    return 50;
  } else if (width >= 800) {
    return 40;
  }
  return 20;
}


const Histogram: React.FC<HistogramProps> = ({ timestamps }) => {
  const now = new Date();
  const todayNoon = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  const previousNoon = new Date(todayNoon);
  previousNoon.setDate(previousNoon.getDate() - 1);

  const [zoomDomain, setZoomDomain] = useState<[Date, Date]>([previousNoon, todayNoon]);
  const [minRangeReached, setMinRangeReached] = useState(false);
  const [maxRangeReached, setMaxRangeReached] = useState(false);

  const width = useResponsiveWidth();
  const height = 400;
  const margin = { top: 20, right: 30, bottom: 30, left: 40 };

  const xScale = useMemo(() => {
    return scaleTime({
      domain: zoomDomain,
      range: [margin.left, width - margin.right],
    });
  }, [zoomDomain, width]);

  const histogramData = useMemo(() => {
    const domain = xScale.domain();
    const ticks = getTicksFromWidth(width);
    const thresholds = xScale.ticks(ticks).map(t => t.getTime());
    const bins = d3Histogram()
      .domain([domain[0].getTime(), domain[1].getTime()])
      .thresholds(thresholds)(timestamps);
    return bins;
  }, [timestamps, xScale, width]);

  const maxBinSize = Math.max(...histogramData.map((bin) => bin.length));
  const numYVals =
    maxBinSize > 300
    ? (maxBinSize - maxBinSize % 50) + 100
    : (
      maxBinSize > 100
      ? (maxBinSize - maxBinSize % 50) + 50
      : (maxBinSize - maxBinSize % 10) + 10
    )

  const numYTicks =
    numYVals > 100
    ? numYVals / 50
    : Math.max(2, numYVals / 10);
    
  const yScale = useMemo(() => {
    return scaleLinear({
      domain: [0, numYVals],
      range: [height - margin.bottom, margin.top],
    });
  }, [histogramData]);

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
  
  const {
    showTooltip,
    hideTooltip,
    tooltipLeft,
    tooltipTop,
    tooltipData,
    tooltipOpen,
  } = useTooltip();

  const handleMouseEnter = useCallback(
    (target: SVGRectElement, numTaps: number, width: number) => {
      showTooltip({
        tooltipLeft: target.x.baseVal.value + width / 2 + 1,
        tooltipTop: target.y.baseVal.value - margin.top / 2,
        tooltipData: `${numTaps} taps`,
      })
    }, [xScale, showTooltip]
  );

  const handleMouseLeave = useCallback(hideTooltip, [hideTooltip]);

  return (
    <>
      <div className="flex justify-end">
        <button
          className="button button-lg button-secondary"
          onClick={panLeft}>
            <KeyboardArrowLeftIcon />
        </button>
        <button
          className="button button-lg button-secondary mr-2"
          onClick={panRight}>
            <KeyboardArrowRightIcon />
        </button>
        <button
          className="button button-lg button-secondary"
          onClick={zoomIn}
          disabled={minRangeReached}>
            <AddIcon />
        </button>
        <button
          className="button button-lg button-secondary mr-2"
          onClick={zoomOut}
          disabled={maxRangeReached}>
            <RemoveIcon />
        </button>
        <button
          className="button button-lg button-primary"
          onClick={resetZoom}>
            <ReplayIcon />
        </button>
      </div>

      <div className="flex justify-center">
        <div className="relative">
          <svg width={width} height={height}>
            <rect width={width} height={height} fill="white" />
            <GridRows
              scale={yScale}
              left={margin.left}
              width={width - margin.left - margin.right}
              height={height - margin.bottom}
              stroke="#e0e0e0"
              numTicks={numYTicks} />
            <GridColumns
              scale={xScale}
              top={margin.top}
              width={width - margin.left - margin.right}
              height={height - margin.bottom}
              stroke="#e0e0e0" />

            <Brush
              xScale={xScale}
              yScale={yScale}
              width={width - margin.left - margin.right}
              height={height - margin.bottom}
              onBrushEnd={(bounds: Bounds | null) => {
                if (bounds) {
                  onZoomChange([bounds.x0, bounds.x1]);
                }
              }}
              resetOnEnd={true} />

            {
              histogramData.map((bin, index) => {
                const width = Math.max(0, xScale(bin.x1 ? bin.x1 : 0) - xScale(bin.x0 ? bin.x0 : 0) - 1);
                return (
                  <Bar
                    key={`bar-${index}`}
                    x={xScale(bin.x0 ? bin.x0 : 0) ?? 0}
                    y={yScale(bin.length)}
                    height={yScale(0) - yScale(bin.length)}
                    width={width}
                    fill="#33334D"
                    onMouseEnter={(e) => handleMouseEnter(e.target as SVGRectElement, bin.length, width)}
                    onMouseLeave={handleMouseLeave} />
                  );
                }
              )
            }

            <AxisBottom top={height - margin.bottom} scale={xScale} />
            <AxisLeft
              left={margin.left}
              scale={yScale}
              numTicks={numYTicks} />
          </svg>
          {
            tooltipOpen &&
            <Tooltip
              key={Math.random()}
              left={(tooltipLeft || 0)}
              top={(tooltipTop || 0)}
              style={{
                ...defaultStyles,
                ...{
                  color: "black",
                  borderTopWidth: 1,
                  borderTopStyle: "solid",
                  borderTopColor: "#33334D",
                  borderRadius: 0,
                }
              }}>
                {tooltipData}
            </Tooltip>
          }
        </div>
      </div>
    </>
  );
};

export default Histogram;
