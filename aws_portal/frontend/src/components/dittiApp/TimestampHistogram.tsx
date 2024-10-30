import React, { useState, useMemo } from 'react';
import { scaleTime, scaleLinear } from '@visx/scale';
import { Bar } from '@visx/shape';
import { Brush } from '@visx/brush';
import { AxisLeft, AxisBottom } from '@visx/axis';
import { bin as d3Histogram } from 'd3-array';
import { Bounds } from '@visx/brush/lib/types';
import { Group } from '@visx/group';
import { GridRows, GridColumns } from '@visx/grid';

interface HistogramProps {
  timestamps: number[];
}


const Histogram: React.FC<HistogramProps> = ({ timestamps }) => {
  const now = new Date();
  const todayNoon = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  const previousNoon = new Date(todayNoon);
  previousNoon.setDate(previousNoon.getDate() - 1);

  const [zoomDomain, setZoomDomain] = useState<[Date, Date]>([previousNoon, todayNoon]);
  const [minRangeReached, setMinRangeReached] = useState(false);
  const [maxRangeReached, setMaxRangeReached] = useState(false);

  const width = 600;
  const height = 400;
  const margin = { top: 20, right: 30, bottom: 30, left: 40 };

  const xScale = useMemo(() => {
    const scale = scaleTime({
      domain: zoomDomain,
      range: [margin.left, width - margin.right],
    });
    return scale;
  }, [zoomDomain]);

  const histogramData = useMemo(() => {
    const domain = xScale.domain();
    const thresholds = xScale.ticks(40).map(t => t.getTime());
    const bins = d3Histogram()
      .domain([domain[0].getTime(), domain[1].getTime()])
      .thresholds(thresholds)(timestamps);

    return bins;
  }, [timestamps, xScale]);

  const numYVals = Math.max(...histogramData.map((bin) => bin.length));

  const yScale = useMemo(() => {
    return scaleLinear({
      domain: [0, numYVals + 10 - numYVals % 10],
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

  return (
    <React.Fragment>
      <button
        className="button button-lg button-primary font-bold"
        onClick={resetZoom}>
          Reset
      </button>
      <button
        className="button button-lg button-primary font-bold"
        onClick={panLeft}>
          Left
      </button>
      <button
        className="button button-lg button-primary font-bold"
        onClick={panRight}>
          Right
      </button>
      <button
        className="button button-lg button-primary font-bold"
        onClick={zoomIn}
        disabled={minRangeReached}>
          Zoom In
      </button>
      <button
        className="button button-lg button-primary font-bold"
        onClick={zoomOut}
        disabled={maxRangeReached}>
          Zoom Out
      </button>

      <svg width={width} height={height}>
        <rect width={width} height={height} fill="white" />
        <GridRows
          scale={yScale}
          left={margin.left}
          width={width - margin.left - margin.right}
          height={height - margin.bottom}
          stroke="#e0e0e0"
          numTicks={numYVals / 10} />
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

        <Group>
          {
            histogramData.map((bin, index) => (
              <Bar
                key={`bar-${index}`}
                x={xScale(bin.x0 ? bin.x0 : 0) ?? 0}
                y={yScale(bin.length)}
                height={yScale(0) - yScale(bin.length)}
                width={Math.max(0, xScale(bin.x1 ? bin.x1 : 0) - xScale(bin.x0 ? bin.x0 : 0) - 1)}
                fill="#33334D" />
            ))
          }

          <AxisBottom top={height - margin.bottom} scale={xScale} />
          <AxisLeft
            left={margin.left}
            scale={yScale}
            numTicks={numYVals / 10} />
        </Group>
      </svg>
    </React.Fragment>
  );
};

export default Histogram;
