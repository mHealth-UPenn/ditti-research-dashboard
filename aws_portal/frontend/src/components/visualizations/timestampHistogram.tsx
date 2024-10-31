import React, { useMemo, useCallback } from 'react';
import { scaleLinear } from '@visx/scale';
import { Bar } from '@visx/shape';
import { Brush } from '@visx/brush';
import { AxisLeft, AxisBottom } from '@visx/axis';
import { bin as d3Histogram } from 'd3-array';
import { Bounds } from '@visx/brush/lib/types';
import { GridRows, GridColumns } from '@visx/grid';
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip"

import { useVisualizationContext } from '../../contexts/visualizationContext';

interface TimestampHistogramProps {
  timestamps: number[];
}


const TimestampHistogram: React.FC<TimestampHistogramProps> = ({ timestamps }) => {
  const {
    width,
    height,
    margin,
    xScale,
    xTicks,
    onZoomChange,
  } = useVisualizationContext();
  // Guard against null xScale
  if (!xScale) return <></>;

  const histogramData = useMemo(() => {
    const domain = xScale.domain();
    const thresholds = xScale.ticks(xTicks).map(t => t.getTime());
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
    }, [showTooltip]
  );

  const handleMouseLeave = useCallback(hideTooltip, [hideTooltip]);

  return (
    <>
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
          height={height - margin.bottom - margin.top}
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

        <AxisBottom
          top={height - margin.bottom}
          scale={xScale}
          label="Time"
          labelClassName="text-lg font-bold"
          labelOffset={20} />
        <AxisLeft
          left={margin.left}
          scale={yScale}
          numTicks={numYTicks}
          label="Taps"
          labelClassName="text-lg font-bold"
          labelOffset={30} />
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
    </>
  );
};

export default TimestampHistogram;
