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

import { useMemo, useCallback } from "react";
import { scaleLinear } from "@visx/scale";
import { Bar } from "@visx/shape";
import { Brush } from "@visx/brush";
import { AxisLeft, AxisBottom } from "@visx/axis";
import { bin as d3Histogram } from "d3-array";
import { Bounds } from "@visx/brush/lib/types";
import { GridRows, GridColumns } from "@visx/grid";
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip";

import { useVisualization } from "../../hooks/useVisualization";
import { colors } from "../../colors";
import { NumberValue } from "d3";
import { TimestampHistogramProps } from "./visualizations.types";

/**
 * Formats ticks for the visualization in `H:MM AM/PM` format. The first tick of the visualization will show the day
 * (Monday, Tuesday, etc.).
 * @param v: The date to format a tick for.
 * @param i: The tick's index.
 * @returns: string - The formatted date.
 */
const formatTick = (v: Date | NumberValue, i: number): string => {
  const date = new Date(v.valueOf());
  const day = date.toLocaleDateString("en-US", { weekday: "long" });
  if (!(i && date.getHours() + date.getMinutes() + date.getSeconds())) {
    return day;
  }
  const time = date.toLocaleTimeString("en-US", {
    hour12: true,
    hour: "numeric",
    minute: "numeric",
  });
  return time;
};

/**
 * Get the timezone of a tick on the visualization. Given the tick `v` and a list of `timezones`, return the name of the
 * first timezone that appears after the tick. If no timezones appear after the tick, return the last timezone.
 * @param v: The date to retrieve the timezone for.
 * @param timezones: The list of timezones.
 * @returns: string - The name of the timezone.
 */
const formatTimeZoneTick = (
  v: Date | NumberValue,
  timezones?: { time: number; name: string }[]
): string => {
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

export const TimestampHistogram = ({
  timestamps,
  timezones,
  marginTop,
  marginRight,
  marginBottom,
  marginLeft,
}: TimestampHistogramProps) => {
  const { width, height, defaultMargin, xScale, xTicks, onZoomChange } =
    useVisualization();

  // Override the default margin if any was passed as props.
  const margin = {
    top: marginTop !== undefined ? marginTop : defaultMargin.top,
    right: marginRight !== undefined ? marginRight : defaultMargin.right,
    bottom: marginBottom !== undefined ? marginBottom : defaultMargin.bottom,
    left: marginLeft !== undefined ? marginLeft : defaultMargin.left,
  };

  // Bin the histogram data using `xScale`
  const histogramData = useMemo(() => {
    const domain = xScale ? xScale.domain() : [];
    const thresholds = xScale
      ? xScale.ticks(xTicks).map((t) => t.getTime())
      : [];
    const bins = d3Histogram()
      .domain([domain[0].getTime(), domain[1].getTime()])
      .thresholds(thresholds)(timestamps);
    return bins;
  }, [timestamps, xScale, width]);

  // Get the largest bin the the histogram
  const maxBinSize = Math.max(...histogramData.map((bin) => bin.length));

  // Define the height of the visualization depending on the largest bin
  const numYVals =
    maxBinSize > 300
      ? maxBinSize - (maxBinSize % 50) + 100
      : maxBinSize > 100
        ? maxBinSize - (maxBinSize % 50) + 50
        : maxBinSize - (maxBinSize % 10) + 10;

  // Define the number of y ticks depending on the height of the histogram
  const numYTicks = numYVals > 100 ? numYVals / 50 : Math.max(2, numYVals / 10);

  // Define the `yScale` of the
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
  } = useTooltip<string>();

  // Show the tooltip when hovering over a bin, if any
  const handleMouseEnter = useCallback(
    (target: SVGRectElement, numTaps: number, width: number) => {
      showTooltip({
        tooltipLeft: target.x.baseVal.value + width / 2 + 1,
        tooltipTop: target.y.baseVal.value - margin.top / 2,
        tooltipData: `${numTaps} taps`,
      });
    },
    [showTooltip]
  );

  // Hide the tooltip when not hovering over a bin
  const handleMouseLeave = useCallback(hideTooltip, [hideTooltip]);

  // Get all midnight timestamps that are visible in `xScale`
  const getMidnightDates = () => {
    const start = xScale ? xScale.domain()[0] : new Date();
    const stop = xScale ? xScale.domain()[1] : new Date();

    const midnightDates = [];

    // Set the start time to midnight
    start.setHours(0, 0, 0, 0);

    while (start <= stop) {
      midnightDates.push(new Date(start)); // Push a copy of the current date
      start.setDate(start.getDate() + 1); // Move to the next day
    }

    return midnightDates;
  };

  if (!xScale) return <></>;

  return (
    <div className="relative">
      <svg width={width} height={height}>
        {/* The visualization background */}
        <rect width={width} height={height} fill="white" />

        {/* Grid rows and columns, including bold columns on midnight timestamps */}
        <GridRows
          scale={yScale}
          left={margin.left}
          width={width - margin.left - margin.right}
          height={height - margin.bottom}
          stroke={colors.extraLight}
          numTicks={numYTicks}
        />
        <GridColumns
          scale={xScale}
          top={margin.top}
          width={width - margin.left - margin.right}
          height={height - margin.bottom - margin.top}
          stroke={colors.extraLight}
        />
        <GridColumns
          scale={xScale}
          top={margin.top}
          width={width - margin.left - margin.right}
          height={height - margin.bottom - margin.top}
          stroke={colors.light}
          strokeWidth={2}
          tickValues={getMidnightDates()}
        />

        {/* Draggable brush for zooming in */}
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
          resetOnEnd={true}
        />

        {/* The bins of the histogram visualization */}
        {histogramData.map((bin, index) => {
          const width = Math.max(
            0,
            xScale(bin.x1 ? bin.x1 : 0) - xScale(bin.x0 ? bin.x0 : 0) - 1
          );
          return (
            <Bar
              key={`bar-${index}`}
              x={xScale(bin.x0 ? bin.x0 : 0) ?? 0}
              y={yScale(bin.length)}
              height={yScale(0) - yScale(bin.length)}
              width={width}
              fill={colors.secondary}
              onMouseEnter={(e) => {
                handleMouseEnter(e.target as SVGRectElement, bin.length, width);
              }}
              onMouseLeave={handleMouseLeave}
            />
          );
        })}

        {/* Bottom axis with weekday and timestamps */}
        <AxisBottom
          top={height - margin.bottom}
          scale={xScale}
          tickLabelProps={{ angle: 45, dx: -5, textAnchor: "start" }}
          tickFormat={formatTick}
        />

        {/* Bottom axis to show the timezone at the first tick of `xScale` */}
        {timezones && (
          <AxisBottom
            top={height - margin.bottom}
            scale={xScale}
            tickLabelProps={{ dy: 55, textAnchor: "start" }}
            tickFormat={(v) => formatTimeZoneTick(v, timezones)}
            tickValues={[xScale.domain()[0]]}
          />
        )}

        {/* Vertical axis with title */}
        <AxisLeft
          left={margin.left}
          scale={yScale}
          numTicks={numYTicks}
          label="Taps"
          labelClassName="text-lg font-bold"
          labelOffset={30}
          tickLabelProps={{ className: "text-xs" }}
        />
      </svg>

      {/* Tooltip to show on hover, if any */}
      {tooltipOpen && (
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
            },
          }}
        >
          {tooltipData}
        </Tooltip>
      )}
    </div>
  );
};
