import React from "react";
import { Line } from "@visx/shape";
import { Group } from "@visx/group";
import { Text } from "@visx/text";
import { AxisBottom } from "@visx/axis";
import { ScaleTime } from "d3";

type GroupData = {
  start: Date;
  stop?: Date;
  label?: string;
};

type TimelineProps = {
  groups: GroupData[];
  width: number;
  height: number;
  margin: { top: number; right: number; bottom: number; left: number };
  xScale: ScaleTime<number, number>;
};


const Timeline: React.FC<TimelineProps> = ({
  groups,
  width,
  height,
  margin,  // = { top: 20, right: 20, bottom: 50, left: 40 },
  xScale
}) => {
  const innerHeight = height - margin.top - margin.bottom;

  const visualizations = groups.map((group, index) => {
    const startX = xScale(group.start);
    const stopX = group.stop ? xScale(group.stop) : startX;
    const y = index * 30; // Spacing each group vertically

    return (
      <Group key={index}>
        {group.stop ? (
          // Draw a line if `stop` exists
          <Line from={{ x: startX, y }} to={{ x: stopX, y }} stroke="black" strokeWidth={2} />
        ) : (
          // Draw a point if only `start` exists
          <circle cx={startX} cy={y} r={5} fill="black" />
        )}
        {/* Display label if provided */}
        {group.label && (
          <Text x={startX} y={y - 10} dy=".33em" fontSize={10} textAnchor="middle">
            {group.label}
          </Text>
        )}
      </Group>
    );
  })

  return (
    <svg width={width} height={height}>
      <Group left={margin.left} top={margin.top}>
        {visualizations}
        {/* Time axis */}
        <AxisBottom top={innerHeight} scale={xScale} />
      </Group>
    </svg>
  );
};

export default Timeline;
