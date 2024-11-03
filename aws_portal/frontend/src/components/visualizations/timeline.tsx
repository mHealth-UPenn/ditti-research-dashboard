import React, { useCallback } from "react";
import { Line } from "@visx/shape";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { scaleLinear } from '@visx/scale';
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { defaultStyles, Tooltip, useTooltip } from "@visx/tooltip"

type GroupData = {
  start: number;
  stop?: number;
  label?: string;
};

type TimelineProps = {
  groups: GroupData[];
  title: string;
  hideAxis?: boolean;
};


const Timeline: React.FC<TimelineProps> = ({
  groups,
  title
}) => {
  const {
    width,
    margin,
    xScale,
  } = useVisualizationContext();
  if (!xScale) return <></>;

  const height = margin.top + margin.bottom;
  const start = xScale.domain()[0].getTime();
  const stop = xScale.domain()[1].getTime();
  
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

  const visualizations = groups
    .filter(group =>
      (start <= group.start && group.start <= stop)
      || (group.stop && start <= group.stop && group.stop <= stop)
      || (group.stop && group.start <= start && stop <= group.stop)
    ).map((group, i) => {
      const startX = Math.max(margin.left, xScale(group.start));
      const stopX = group.stop ? Math.min(xScale(group.stop), width - margin.right) : startX;
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
            {group.start >= start && <circle cx={startX} cy={y} r={5} fill="black" />}
            <Line from={{ x: startX, y }} to={{ x: stopX, y }} stroke="black" strokeWidth={2} />
            {stop >= group.stop && <circle cx={stopX} cy={y} r={5} fill="black" />}
            {tooltipRect}
          </React.Fragment>
        );
      }
      return (
        <React.Fragment key={i}>
          <circle cx={startX} cy={y} r={5} fill="black" />
          {tooltipRect}
        </React.Fragment>
      );
  });

  return (
    <div className="relative">
      <svg width={width} height={height}>
        <AxisBottom top={margin.top} scale={xScale} />
        <AxisLeft
          left={margin.left}
          scale={scaleLinear({domain: [0, 0], range: [margin.top, margin.top]})}
          numTicks={0}
          label={title}
          labelClassName="text-lg font-bold"
          labelOffset={30} />
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
              borderTopColor: "#33334D",
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
