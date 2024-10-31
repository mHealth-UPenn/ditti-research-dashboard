import React from "react";
import { Line } from "@visx/shape";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { scaleLinear } from '@visx/scale';
import { useVisualizationContext } from "../../contexts/visualizationContext";

type GroupData = {
  start: number;
  stop?: number;
  label?: string;
};

type TimelineProps = {
  groups: GroupData[];
};


const Timeline: React.FC<TimelineProps> = ({ groups }) => {
  const {
    width,
    margin,
    xScale,
  } = useVisualizationContext();
  if (!xScale) return <></>;

  margin.top = 40;
  const height = margin.top + margin.bottom;
  const start = xScale.domain()[0].getTime();
  const stop = xScale.domain()[1].getTime();

  const visualizations = groups
    .filter(group =>
      (start <= group.start && group.start <= stop)
      || (group.stop && start <= group.stop && group.stop <= stop)
      || (group.stop && group.start <= start && stop <= group.stop)
    ).map(group => {
      const startX = Math.max(margin.left, xScale(group.start));
      const stopX = group.stop ? Math.min(xScale(group.stop), width - margin.right) : startX;
      const y = margin.top;

      if (group.stop) {
        return (
          <>
            {group.start >= start && <circle cx={startX} cy={y} r={5} fill="black" />}
            <Line from={{ x: startX, y }} to={{ x: stopX, y }} stroke="black" strokeWidth={2} />
            {stop >= group.stop && <circle cx={stopX} cy={y} r={5} fill="black" />}
          </>
        );
      }
      return <circle cx={startX} cy={y} r={5} fill="black" />;
  });

  return (
    <svg width={width} height={height}>
      {visualizations}
      <AxisBottom top={margin.top} scale={xScale} />
      <AxisLeft
        left={margin.left}
        scale={scaleLinear({domain: [0, 0], range: [margin.top, margin.top]})}
        numTicks={0}
        label="Bouts"
        labelClassName="text-lg font-bold"
        labelOffset={30} />
    </svg>
  );
};

export default Timeline;
