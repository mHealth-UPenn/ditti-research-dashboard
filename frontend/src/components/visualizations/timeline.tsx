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

import React, { useCallback } from "react";
import { Line } from "@visx/shape";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { scaleLinear } from "@visx/scale";
import { useVisualization } from "../../hooks/useVisualization";
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip";
import { colors } from "../../colors";
import { TimelineProps } from "./visualizations.types";

export const Timeline = ({
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
}: TimelineProps) => {
  const { width, defaultMargin, xScale } = useVisualization();

  const margin = {
    top: marginTop ?? defaultMargin.top,
    right: marginRight ?? defaultMargin.right,
    bottom: marginBottom ?? defaultMargin.bottom,
    left: marginLeft ?? defaultMargin.left,
  };

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
  } = useTooltip<string>();

  // Show `label` text on mouse hover.
  const handleMouseEnter = useCallback(
    (target: SVGRectElement, label: string) => {
      showTooltip({
        tooltipLeft: target.x.baseVal.value,
        tooltipTop: 0,
        tooltipData: label,
      });
    },
    [showTooltip]
  );

  const handleMouseLeave = useCallback(() => {
    hideTooltip();
  }, [hideTooltip]);

  const visualizations = !xScale
    ? []
    : // Get only groups that either start or stop within the timeline range
      groups
        .filter((group) => {
          const startInRange = start <= group.start && group.start <= stop;
          const stopInRange =
            group.stop != null && start <= group.stop && group.stop <= stop;
          const spansRange =
            group.stop != null && group.start <= start && stop <= group.stop;
          return startInRange || stopInRange || spansRange;
        })
        .map((group, i) => {
          // The group's position
          const startX = Math.max(
            margin.left,
            xScale(group.start - xScaleOffset)
          );
          const stopX = group.stop
            ? Math.min(xScale(group.stop - xScaleOffset), width - margin.right)
            : startX;
          const y = margin.top;

          // The tooltip to display on hover if `label` exists.
          const tooltipRect = group.label ? (
            <rect
              x={startX - 10}
              y={margin.top - 15}
              width={stopX - startX + 20}
              height={30}
              fill="transparent"
              onMouseEnter={(e) => {
                if (group.label) {
                  handleMouseEnter(e.target as SVGRectElement, group.label);
                }
              }}
              onMouseLeave={handleMouseLeave}
            />
          ) : (
            <></>
          );

          // If `stop` exists, create a range
          if (group.stop) {
            return (
              <React.Fragment key={i}>
                {!hideStops && group.start >= start && (
                  <circle
                    cx={startX}
                    cy={y}
                    r={5}
                    fill={group.color ?? color}
                  />
                )}
                <Line
                  from={{ x: startX, y }}
                  to={{ x: stopX, y }}
                  stroke={group.color ?? color}
                  strokeWidth={strokeWidth}
                  strokeDasharray={group.strokeDashArray ?? strokeDashArray}
                />
                {!hideStops && stop >= group.stop && (
                  <circle cx={stopX} cy={y} r={5} fill={group.color ?? color} />
                )}
                {tooltipRect}
              </React.Fragment>
            );
          }

          // Create a single point
          return (
            <React.Fragment key={i}>
              {!hideStops && (
                <circle cx={startX} cy={y} r={5} fill={group.color ?? color} />
              )}
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
          tickLineProps={hideTicks ? { display: "none" } : {}}
          tickLabelProps={hideAxis ? { display: "none" } : {}}
          stroke={axisColor}
        />

        {/* A left axis for displaying the title, if one was passed */}
        {title && (
          <AxisLeft
            left={margin.left}
            scale={scaleLinear({
              domain: [0, 0],
              range: [margin.top, margin.top],
            })}
            numTicks={0}
            label={title}
            labelClassName="text-lg font-bold"
            labelOffset={30}
          />
        )}

        {/* The data to display on the timeline */}
        {visualizations}
      </svg>

      {/* The tooltip to show on mouse hover, if any */}
      {tooltipOpen && (
        <Tooltip
          key={Math.random()}
          left={tooltipLeft ?? 0}
          top={tooltipTop ?? 0}
          style={{
            ...defaultStyles,
            ...{
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
