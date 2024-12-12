import React, { useCallback } from "react";
import { Line } from "@visx/shape";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { scaleLinear } from '@visx/scale';
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip"
import colors from "../../colors";
import { IVisualizationProps } from "../../interfaces";

type GroupData = {
  start: number;
  stop?: number;
  label?: string;
};

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
  if (!xScale) return <></>;

  const margin = {
    top: marginTop !== undefined ? marginTop : defaultMargin.top,
    right: marginRight !== undefined ? marginRight : defaultMargin.right,
    bottom: marginBottom !== undefined ? marginBottom : defaultMargin.bottom,
    left: marginLeft !== undefined ? marginLeft : defaultMargin.left,
  }

  const height = margin.top + margin.bottom;
  const start = xScale.domain()[0].getTime() + xScaleOffset;
  const stop = xScale.domain()[1].getTime() + xScaleOffset;
  
  const {
    showTooltip,
    hideTooltip,
    tooltipLeft,
    tooltipTop,
    tooltipData,
    tooltipOpen,
  } = useTooltip();

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

  // if (groups.length) {
  //   console.log(new Date(groups[0].start), new Date(groups[0].stop!))
  //   console.log(new Date(start), new Date(stop))
  // }
  const visualizations = groups
    .filter(group =>
      (start <= group.start && group.start <= stop)
      || (group.stop && start <= group.stop && group.stop <= stop)
      || (group.stop && group.start <= start && stop <= group.stop)
    ).map((group, i) => {
      const startX = Math.max(margin.left, xScale(group.start - xScaleOffset));
      const stopX = group.stop ? Math.min(xScale(group.stop - xScaleOffset), width - margin.right) : startX;
      const y = margin.top;
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

      if (group.stop) {
        return (
          <React.Fragment key={i}>
            {!hideStops && group.start >= start && <circle cx={startX} cy={y} r={5} fill={color} />}
            <Line from={{ x: startX, y }} to={{ x: stopX, y }} stroke={color} strokeWidth={strokeWidth} strokeDasharray={strokeDashArray} />
            {!hideStops && stop >= group.stop && <circle cx={stopX} cy={y} r={5} fill={color} />}
            {tooltipRect}
          </React.Fragment>
        );
      }
      return (
        <React.Fragment key={i}>
          {!hideStops && <circle cx={startX} cy={y} r={5} fill={color} />}
          {tooltipRect}
        </React.Fragment>
      );
  });

  return (
    <div className="relative">
      <svg width={width} height={height}>
        <AxisBottom
          top={margin.top}
          scale={xScale}
          axisLineClassName=""
          tickLineProps={hideTicks ? { display: "none" } : { }}
          tickLabelProps={hideAxis ? { display: "none" } : { }}
          stroke={axisColor} />
        {title &&
          <AxisLeft
            left={margin.left}
            scale={scaleLinear({domain: [0, 0], range: [margin.top, margin.top]})}
            numTicks={0}
            label={title}
            labelClassName="text-lg font-bold"
            labelOffset={30} />
        }
        {visualizations}
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
