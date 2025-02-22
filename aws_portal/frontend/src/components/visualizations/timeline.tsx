/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import React, { useCallback } from "react";
import { Line } from "@visx/shape";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { scaleLinear } from '@visx/scale';
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip"
import colors from "../../colors";
import { IVisualizationProps } from "../../interfaces";


/**
 * Either a single point or range on the timeline.
 * @property start: A timestamp representing a single point or the start of a range.
 * @property stop: An optional timestamp representing the end of a range.
 * @property label: An optional label to display on hover.
 * @property strokeDashArray: An optional stroke dash array to pas to `Line`.
 * @property color: An optional color to display the point or range as.
 */
type GroupData = {
  start: number;
  stop?: number;
  label?: string;
  strokeDashArray?: string;
  color?: string;
};


/**
 * Props for the `Timeline` visualization.
 * @property groups: An array of `GroupData` representing points or ranges to display on the timeline.
 * @property title: A title. Titles are displayed to the left of the timeline and rotated 90 degrees.
 * @property hideAxis: Whether to hide the axis.
 * @property hideStops: Whether to hide start and stop points on ranges.
 * @property hideTicks: Whether to hide ticks on the timeline.
 * @property xScaleOffset: The number of milliseconds to offset data by.
 * @property strokeWidth: The stroke height of ranges.
 * @property color: The default color for points and ranges. This is overridden by any `color` property passed in
 *   `groups`.
 * @property axisColor: The axis color.
 * @property strokeDashArray: The default stroke dash array for ranges. This is overridden by any `strokeDashArray`
 *   property passed in `groups`.
 */
interface TimelineProps extends IVisualizationProps {
  groups: GroupData[];
  title?: string;
  hideAxis?: boolean;
  hideStops?: boolean;
  hideTicks?: boolean;
  xScaleOffset?: number;
  strokeWidth?: number;
  color?: string;
  axisColor?: string;
  strokeDashArray?: string;
}


const Timeline: React.FC<TimelineProps> = ({
  groups,
  title,
  hideAxis,
  hideStops = false,
  hideTicks = false,
  xScaleOffset = 0,
  strokeWidth = 2,
  color = "black",
  axisColor = "black",
  strokeDashArray,
  marginTop,
  marginRight,
  marginBottom,
  marginLeft,
}) => {
  const {
    width,
    defaultMargin,
    xScale,
  } = useVisualizationContext();

  const margin = {
    top: marginTop !== undefined ? marginTop : defaultMargin.top,
    right: marginRight !== undefined ? marginRight : defaultMargin.right,
    bottom: marginBottom !== undefined ? marginBottom : defaultMargin.bottom,
    left: marginLeft !== undefined ? marginLeft : defaultMargin.left,
  }

  const height = margin.top + margin.bottom;
  const start = xScale ? xScale.domain()[0].getTime() + xScaleOffset : 0;
  const stop = xScale ? xScale.domain()[1].getTime() + xScaleOffset : 0;
  
  const {
    showTooltip,
    hideTooltip,
    tooltipLeft,
    tooltipTop,
    tooltipData,
    tooltipOpen,
  } = useTooltip();

  // Show `label` text on mouse hover.
  const handleMouseEnter = useCallback(
    (target: SVGRectElement, label: string) => {
      showTooltip({
        tooltipLeft: target.x.baseVal.value,
        tooltipTop: 0,
        tooltipData: label,
      })
    }, [showTooltip]
  );

  const handleMouseLeave = useCallback(hideTooltip, [hideTooltip]);

  const visualizations = !xScale ? [] : 
    // Get only groups that either start or stop within the timeline range
    groups.filter(group =>
      (start <= group.start && group.start <= stop)
      || (group.stop && start <= group.stop && group.stop <= stop)
      || (group.stop && group.start <= start && stop <= group.stop)
    ).map((group, i) => {
      // The group's position
      const startX = Math.max(margin.left, xScale(group.start - xScaleOffset));
      const stopX = group.stop ? Math.min(xScale(group.stop - xScaleOffset), width - margin.right) : startX;
      const y = margin.top;

      // The tooltip to display on hover if `label` exists.
      const tooltipRect =
        group.label
        ?
          <rect
            x={startX - 10}
            y={margin.top - 15}
            width={stopX - startX + 20}
            height={30}
            fill="transparent"
            onMouseEnter={(e) => group.label && handleMouseEnter(e.target as SVGRectElement, group.label)}
            onMouseLeave={handleMouseLeave} />
        : <></>

      // If `stop` exists, create a range
      if (group.stop) {
        return (
          <React.Fragment key={i}>
            {!hideStops && group.start >= start &&
              <circle cx={startX} cy={y} r={5} fill={group.color || color} />
            }
            <Line
              from={{ x: startX, y }}
              to={{ x: stopX, y }}
              stroke={group.color || color}
              strokeWidth={strokeWidth}
              strokeDasharray={group.strokeDashArray || strokeDashArray} />
            {!hideStops && stop >= group.stop &&
              <circle cx={stopX} cy={y} r={5} fill={group.color || color} />
            }
            {tooltipRect}
          </React.Fragment>
        );
      }

      // Create a single point
      return (
        <React.Fragment key={i}>
          {!hideStops && <circle cx={startX} cy={y} r={5} fill={group.color || color} />}
          {tooltipRect}
        </React.Fragment>
      );
  });

  if (!xScale) return <></>;

  return (
    <div className="relative">
      <svg width={width} height={height}>
        {/* The bottom axis */}
        <AxisBottom
          top={margin.top}
          scale={xScale}
          axisLineClassName=""
          tickLineProps={hideTicks ? { display: "none" } : { }}
          tickLabelProps={hideAxis ? { display: "none" } : { }}
          stroke={axisColor} />

        {/* A left axis for displaying the title, if one was passed */}
        {title &&
          <AxisLeft
            left={margin.left}
            scale={scaleLinear({domain: [0, 0], range: [margin.top, margin.top]})}
            numTicks={0}
            label={title}
            labelClassName="text-lg font-bold"
            labelOffset={30} />
        }

        {/* The data to display on the timeline */}
        {visualizations}
      </svg>

      {/* The tooltip to show on mouse hover, if any */}
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

export default Timeline;
