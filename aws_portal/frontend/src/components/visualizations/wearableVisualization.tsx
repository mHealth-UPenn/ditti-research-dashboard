import colors from "../../colors";
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { useWearableData } from "../../contexts/wearableDataContext";
import { ISleepLevelClassic, ISleepLevelStages } from "../../interfaces";
import Timeline from "./timeline";
import { AxisTop } from "@visx/axis";


const getWeekday = (date: Date) => {
  return date.toLocaleDateString("en-US", { weekday: "long" });
};


type ILevelGroupsStages = Record<ISleepLevelStages, { start: number; stop: number; }[]>;
type ILevelGroupsClassic = Record<ISleepLevelClassic, { start: number; stop: number; }[]>;


const WearableVisualization = () => {
  const { width, xScale } = useVisualizationContext();
  const { sleepLogs, isLoading } = useWearableData();

  if (isLoading || !xScale) {
    return <></>;
  }

  const visualizations = sleepLogs.slice(0, 7).map((sl, i) => {
    const levelGroups: ILevelGroupsStages = {
      wake: [],
      rem: [],
      light: [],
      deep: [],
    };

    sl.levels.forEach(l => {
      levelGroups[l.level as ISleepLevelStages].push({
        start: l.dateTime.getTime(),
        stop: l.dateTime.getTime() + l.seconds * 1000,
      })
    })

    const title = getWeekday(sl.dateOfSleep);
    const offset = (i + 1 - Math.max(7, sleepLogs.length)) * 24 * 60 * 60 * 1000;

    return (
      <div key={i} className="relative flex items-center mb-4">
        <span className="absolute font-bold text-sm [writing-mode:vertical-lr] rotate-180">{title}</span>
        <div>
          <Timeline
            groups={levelGroups.wake}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableWake}
            axisColor={colors.light}
            xScaleOffset={offset} />
          <Timeline
            groups={levelGroups.rem}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableRem}
            axisColor={colors.light}
            xScaleOffset={offset} />
          <Timeline
            groups={levelGroups.light}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableLight}
            axisColor={colors.light}
            xScaleOffset={offset} />
          <Timeline
            groups={levelGroups.deep}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableDeep}
            axisColor={colors.light}
            xScaleOffset={offset} />
          </div>
      </div>
    );
  })

  return (
    <div className="flex flex-col">
      <svg className="relative top-[10px]" width={width} height={40}>
        <AxisTop
          top={38}
          scale={xScale}
          stroke="transparent"
          tickLength={20}
          tickStroke={colors.light} />
      </svg>
      {visualizations}
    </div>
  );
};


export default WearableVisualization;
