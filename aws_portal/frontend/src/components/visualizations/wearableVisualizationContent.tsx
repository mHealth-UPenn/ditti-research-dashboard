import colors from "../../colors";
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { useWearableData } from "../../contexts/wearableDataContext";
import { ISleepLevelClassic, ISleepLevelStages } from "../../interfaces";
import Timeline from "./timeline";
import { AxisTop } from "@visx/axis";
import { GridColumns } from '@visx/grid';
import { Brush } from '@visx/brush';
import { scaleLinear } from '@visx/scale';
import Button from "../buttons/button";
import ReplayIcon from '@mui/icons-material/Replay';


const getWeekday = (date: Date) => {
  return date.toLocaleDateString("en-US", { weekday: "long" });
};


const getTime = (date: Date) => {
  return date.toLocaleTimeString(
    "en-US", { hour12: true, hour: "numeric", minute: "numeric" }
  );
}


type ILevelGroupsStages = Record<ISleepLevelStages, { start: number; stop: number; }[]>;
type ILevelGroupsClassic = Record<ISleepLevelClassic, { start: number; stop: number; }[]>;


const WearableVisualizationContent = () => {
  const { width, margin, xScale, onZoomChange, resetZoom } = useVisualizationContext();
  const { sleepLogs, isLoading } = useWearableData();

  if (isLoading || !xScale) {
    return <></>;
  }

  const visualizations = sleepLogs.slice(0, 7).map((sl, i) => {
    const groups: { start: number; stop: number; }[][] = [];
  
    if (sl.type === "stages") {
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
      });

      groups[0] = levelGroups["wake"];
      groups[1] = levelGroups["rem"];
      groups[2] = levelGroups["light"];
      groups[3] = levelGroups["deep"];
    } else {
      const levelGroups: ILevelGroupsClassic = {
        awake: [],
        restless: [],
        asleep: [],
      };

      sl.levels.forEach(l => {
        levelGroups[l.level as ISleepLevelClassic].push({
          start: l.dateTime.getTime(),
          stop: l.dateTime.getTime() + l.seconds * 1000,
        })
      });

      groups[0] = levelGroups["awake"];
      groups[1] = [];
      groups[2] = levelGroups["restless"];
      groups[3] = levelGroups["asleep"];
    }

    const title = getWeekday(sl.dateOfSleep);
    const offset = (i + 1 - Math.max(7, sleepLogs.length)) * 24 * 60 * 60 * 1000;

    return (
      <div key={i} className="relative flex items-center mb-8">
        <span className="absolute font-bold text-sm [writing-mode:vertical-lr] rotate-180">{title}</span>
        <div>
          <svg className="absolute" width={width} height={80}>
            <GridColumns
              scale={xScale}
              width={width - margin.left - margin.right}
              height={80 - margin.bottom - margin.top}
              stroke={colors.light}
              strokeDasharray="5,5"
              numTicks={window.screen.width > 600 ? 10 : 5} />
          </svg>
          <Timeline
            groups={groups[0]}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableWake}
            axisColor={colors.wearableWake}
            xScaleOffset={offset}
            strokeDashArray={sl.type === "classic" ? "1,1" : ""} />
          <Timeline
            groups={groups[1]}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableRem}
            axisColor={colors.light}
            xScaleOffset={offset}
            strokeDashArray={sl.type === "classic" ? "1,1" : ""} />
          <Timeline
            groups={groups[2]}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableLight}
            axisColor={colors.light}
            xScaleOffset={offset}
            strokeDashArray={sl.type === "classic" ? "1,1" : ""} />
          <Timeline
            groups={groups[3]}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableDeep}
            axisColor={colors.light}
            xScaleOffset={offset}
            strokeDashArray={sl.type === "classic" ? "1,1" : ""} />
          <svg className="absolute top-0" width={width} height={80}>
            <Brush
              xScale={xScale}
              yScale={scaleLinear({domain: [0, 80], range: [0, 80]})}
              width={width}
              height={80 - margin.bottom - margin.top}
              onBrushEnd={bounds => {
                if (bounds) {
                  onZoomChange([bounds.x0, bounds.x1]);
                }
              }}
              resetOnEnd={true} />
          </svg>
        </div>
      </div>
    );
  })

  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <div className="flex flex-col">
          <div className="flex mb-1">
            <span className="text-xs font-bold w-[3rem]">Stages:</span>
            <div className="flex mr-4">
              <div className="bg-wearable-wake w-[1rem] mr-2" />
              <span className="text-xs">Awake</span>
            </div>
            <div className="flex mr-4">
              <div className="bg-wearable-rem w-[1rem] mr-2" />
              <span className="text-xs">REM</span>
            </div>
            <div className="flex mr-4">
              <div className="bg-wearable-light w-[1rem] mr-2" />
              <span className="text-xs">Light</span>
            </div>
            <div className="flex">
              <div className="bg-wearable-deep w-[1rem] mr-2" />
              <span className="text-xs">Deep</span>
            </div>
          </div>
          <div className="flex">
            <span className="text-xs font-bold w-[3rem]">Classic:</span>
            <div className="flex mr-4">
              <div className="bg-[repeating-linear-gradient(90deg,#E04B6F,#E04B6F_1px,transparent_1px,transparent_2px)] w-[1rem] mr-2" />
              <span className="text-xs">Awake</span>
            </div>
            <div className="flex mr-4">
              <div className="bg-[repeating-linear-gradient(90deg,#5489F5,#5489F5_1px,transparent_1px,transparent_2px)] w-[1rem] mr-2" />
              <span className="text-xs">Restless</span>
            </div>
            <div className="flex">
              <div className="bg-[repeating-linear-gradient(90deg,#24499F,#24499F_1px,transparent_1px,transparent_2px)] w-[1rem] mr-2" />
              <span className="text-xs">Asleep</span>
            </div>
          </div>
        </div>
        <Button
          square={true}
          size="sm"
          variant="primary"
          onClick={resetZoom}
          rounded={true}>
            <ReplayIcon />
        </Button>
      </div>
      <svg className="relative top-[10px]" width={width} height={40}>
        <AxisTop
          top={38}
          scale={xScale}
          stroke="transparent"
          tickLength={20}
          tickStroke={colors.light}
          numTicks={window.screen.width > 600 ? 10 : 5}
          tickFormat={v => getTime(v as Date)} />
      </svg>
      {visualizations}
    </div>
  );
};


export default WearableVisualizationContent;
