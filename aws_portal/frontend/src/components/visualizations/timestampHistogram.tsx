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
import colors from '../../colors';
import { NumberValue } from 'd3';
import { IVisualizationProps } from '../../interfaces';

interface TimestampHistogramProps extends IVisualizationProps {
  timestamps: number[];
  timezones?: { time: number; name: string }[];
}


const formatTick = (v: Date | NumberValue, i: number) => {
  const date = new Date(v.valueOf())
  const day = date.toLocaleDateString("en-US", { weekday: "long" });
  if (!(i && date.getHours() + date.getMinutes() + date.getSeconds())) {
    return day;
  }
  const time = date.toLocaleTimeString(
    "en-US", { hour12: true, hour: "numeric", minute: "numeric" }
  );
  return time;
};


const formatTimeZoneTick = (v: Date | NumberValue, timezones?: { time: number; name: string; }[]) => {
  if (!timezones) {
    return "";
  }

  let index = 0;
  while (index < timezones.length && v.valueOf() > timezones[index].time) {
    index++;
  }

  if (index === timezones.length) {
    return timezones[index - 1]?.name || "";
  }
  return timezones[index]?.name || "";
};


const TimestampHistogram = ({
  timestamps,
  timezones,
  marginTop,
  marginRight,
  marginBottom,
  marginLeft,
}: TimestampHistogramProps) => {
  const {
    width,
    height,
    defaultMargin,
    xScale,
    xTicks,
    onZoomChange,
  } = useVisualizationContext();
  // Guard against null xScale
  if (!xScale) return <></>;
  timezones?.forEach(tz => console.log(new Date(tz.time), tz.name))

  const margin = {
    top: marginTop !== undefined ? marginTop : defaultMargin.top,
    right: marginRight !== undefined ? marginRight : defaultMargin.right,
    bottom: marginBottom !== undefined ? marginBottom : defaultMargin.bottom,
    left: marginLeft !== undefined ? marginLeft : defaultMargin.left,
  }

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

  const getMidnightDates = () => {
    const start = xScale.domain()[0];
    const stop = xScale.domain()[1];

    const midnightDates = [];

    // Set the start time to midnight
    start.setHours(0, 0, 0, 0);

    while (start <= stop) {
        midnightDates.push(new Date(start)); // Push a copy of the current date
        start.setDate(start.getDate() + 1); // Move to the next day
    }

    return midnightDates;
  };

  return (
    <div className="relative">
      <svg width={width} height={height}>
        <rect width={width} height={height} fill="white" />
        <GridRows
          scale={yScale}
          left={margin.left}
          width={width - margin.left - margin.right}
          height={height - margin.bottom}
          stroke={colors.extraLight}
          numTicks={numYTicks} />
        <GridColumns
          scale={xScale}
          top={margin.top}
          width={width - margin.left - margin.right}
          height={height - margin.bottom - margin.top}
          stroke={colors.extraLight} />
        <GridColumns
          scale={xScale}
          top={margin.top}
          width={width - margin.left - margin.right}
          height={height - margin.bottom - margin.top}
          stroke={colors.light}
          strokeWidth={2}
          tickValues={getMidnightDates()} />

        <Brush
          xScale={xScale}
          yScale={yScale}
          width={width}
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
                fill={colors.secondary}
                onMouseEnter={(e) => handleMouseEnter(e.target as SVGRectElement, bin.length, width)}
                onMouseLeave={handleMouseLeave} />
              );
            }
          )
        }

        <AxisBottom
          top={height - margin.bottom}
          scale={xScale}
          tickLabelProps={{ angle: 45, dx: -5, textAnchor: "start" }}
          tickFormat={formatTick} />
        {timezones &&
          <AxisBottom
            top={height - margin.bottom}
            scale={xScale}
            tickLabelProps={{ dy: 55, textAnchor: "start" }}
            tickFormat={(v) => formatTimeZoneTick(v, timezones)}
            tickValues={[xScale.domain()[0]]} />
        }
        <AxisLeft
          left={margin.left}
          scale={yScale}
          numTicks={numYTicks}
          label="Taps"
          labelClassName="text-lg font-bold"
          labelOffset={30}
          tickLabelProps={{ className: "text-xs" }} />
      </svg>
      {
        tooltipOpen &&
        <Tooltip
          key={Math.random()}
          left={(tooltipLeft || 0) - 1}
          top={(tooltipTop || 0) + 15}
          style={{
            ...defaultStyles,
            ...{
              height: 25,
              color: "black",
              borderTopWidth: 1,
              borderTopStyle: "solid",
              borderTopColor: colors.secondary,
              borderRadius: 0,
            }
          }}>
            {tooltipData}
        </Tooltip>
      }
    </div>
  );
};

export default TimestampHistogram;
