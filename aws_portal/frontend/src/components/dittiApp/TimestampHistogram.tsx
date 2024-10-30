import React, { useState, useMemo } from 'react';
import { scaleTime, scaleLinear } from '@visx/scale';
import { Bar } from '@visx/shape';
import { Brush } from '@visx/brush';
import { AxisLeft, AxisBottom } from '@visx/axis';
import { bin as d3Histogram } from 'd3-array';
import { Bounds } from '@visx/brush/lib/types';

interface HistogramProps {
  timestamps: number[];
}


const Histogram: React.FC<HistogramProps> = ({ timestamps }) => {
  const [zoomDomain, setZoomDomain] = useState<[Date, Date] | null>(null);
  const width = 800;
  const height = 400;
  const margin = { top: 20, right: 30, bottom: 30, left: 40 };

  const now = new Date();
  const todayNoon = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  const previousNoon = new Date(todayNoon);
  previousNoon.setDate(previousNoon.getDate() - 1);

  const xScale = useMemo(() => {
    const scale = scaleTime({
      domain: zoomDomain ?? [previousNoon, todayNoon],
      range: [margin.left, width - margin.right],
    });
    console.log(scale.domain());
    return scale;
  }, [zoomDomain]);

  const histogramData = useMemo(() => {
    const binSize = calculateBinSize(width);
    const domain = xScale.domain();
    const thresholds = xScale.ticks(binSize).map(t => t.getTime());
    const bins = d3Histogram()
      .domain([domain[0].getTime(), domain[1].getTime()])
      .thresholds(thresholds)(timestamps);

    return bins;
  }, [timestamps, xScale]);

  const yScale = useMemo(() => {
    return scaleLinear({
      domain: [0, Math.max(...histogramData.map((bin) => bin.length))],
      range: [height - margin.bottom, margin.top],
    });
  }, [histogramData]);

  const onZoomChange = (domain: [number, number]) => {
    setZoomDomain([new Date(domain[0]), new Date(domain[1])]);
  };

  const resetZoom = () => setZoomDomain(null);

  return (
    <svg width={width} height={height}>
      <rect width={width} height={height} fill="#f3f3f3" />
      <AxisBottom top={height - margin.bottom} scale={xScale} />
      <AxisLeft left={margin.left} scale={yScale} />

      {
        histogramData.map((bin, index) => (
          <Bar
            key={`bar-${index}`}
            x={xScale(bin.x0 ? bin.x0 : 0) ?? 0}
            y={yScale(bin.length)}
            height={yScale(0) - yScale(bin.length)}
            width={Math.max(0, xScale(bin.x1 ? bin.x1 : 0) - xScale(bin.x0 ? bin.x0 : 0))}
            fill="teal" />
        ))
      }

      <Brush
        xScale={xScale}
        yScale={yScale}
        width={width - margin.left - margin.right}
        height={height - margin.top - margin.bottom}
        onBrushEnd={(bounds: Bounds | null) => {
          if (bounds) {
            onZoomChange([bounds.x0, bounds.x1]);
          }
        }}
        resetOnEnd={true} />
      <foreignObject x={20} y={20} width={70} height={60}>
        <button onClick={resetZoom}>Reset Zoom</button>
      </foreignObject>
    </svg>
  );
};

// Utility function to calculate bin size based on window width
function calculateBinSize(width: number) {
  if (width > 1200) return 1; // 1-minute bin size
  if (width > 800) return 5; // 5-minute bin size
  if (width > 500) return 15; // 15-minute bin size
  return 60; // hourly bin size
}

export default Histogram;
