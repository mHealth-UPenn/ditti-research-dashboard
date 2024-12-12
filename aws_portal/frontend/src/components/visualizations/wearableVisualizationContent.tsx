import colors from "../../colors";
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { useWearableData } from "../../contexts/wearableDataContext";
import { ISleepLevelClassic, ISleepLevelStages, ISleepLog, IVisualizationProps } from "../../interfaces";
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

interface IGroup { start: number; stop: number; strokeDashArray: string; }
type ILevelGroupsStages = Record<ISleepLevelStages, IGroup[]>;
type ILevelGroupsClassic = Record<ISleepLevelClassic, IGroup[]>;


const WearableVisualizationContent = ({
  marginTop,
  marginRight,
  marginBottom,
  marginLeft,
}: IVisualizationProps) => {
  const {
    width,
    xScale,
    defaultMargin,
    onZoomChange,
    resetZoom
  } = useVisualizationContext();
  const { sleepLogs, isLoading } = useWearableData();

  const margin = {
    top: marginTop !== undefined ? marginTop : defaultMargin.top,
    right: marginRight !== undefined ? marginRight : defaultMargin.right,
    bottom: marginBottom !== undefined ? marginBottom : defaultMargin.bottom,
    left: marginLeft !== undefined ? marginLeft : defaultMargin.left,
  }

  if (isLoading || !xScale) {
    return <></>;
  }

  // Group sleep logs by date to handle cases where there are more than one on a day
  const days: { [key: string]: ISleepLog[] } = {};
  sleepLogs.forEach(sl => {
    if (sl.dateOfSleep in days) {
      days[sl.dateOfSleep].push(sl);
    } else {
      days[sl.dateOfSleep] = [sl];
    }
  });

  const visualizations = Object.values(days).map((sleepLogs, i) => {
    const row1: IGroup[] = [];  // awake
    const row2: IGroup[] = [];  // rem (if available)
    const row3: IGroup[] = [];  // light or restless
    const row4: IGroup[] = [];  // deep or asleep

    sleepLogs.forEach(sl => {
      const dateOfSleep = new Date(sl.dateOfSleep);
    
      if (sl.type === "stages") {
        const levelGroups: ILevelGroupsStages = {
          wake: [],
          rem: [],
          light: [],
          deep: [],
        };

        sl.levels.forEach(l => {
          const dateTime = new Date(l.dateTime);

          levelGroups[l.level as ISleepLevelStages].push({
            start: dateTime.getTime(),
            stop: dateTime.getTime() + l.seconds * 1000,
            strokeDashArray: "",
          })
        });

        row1.push(...levelGroups.wake);
        row2.push(...levelGroups.rem);
        row3.push(...levelGroups.light);
        row4.push(...levelGroups.deep);
      } else {
        const levelGroups: ILevelGroupsClassic = {
          awake: [],
          restless: [],
          asleep: [],
        };

        sl.levels.forEach(l => {
          const dateTime = new Date(l.dateTime);

          levelGroups[l.level as ISleepLevelClassic].push({
            start: dateTime.getTime(),
            stop: dateTime.getTime() + l.seconds * 1000,
            strokeDashArray: "1,1",
          })
        });

        row1.push(...levelGroups.awake);
        row3.push(...levelGroups.restless);
        row4.push(...levelGroups.asleep);
      }
    });

    const title = getWeekday(new Date(sleepLogs[0].dateOfSleep));
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
            groups={row1}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableWake}
            axisColor={colors.light}
            xScaleOffset={offset} />
          <Timeline
            groups={row2}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableRem}
            axisColor={colors.light}
            xScaleOffset={offset} />
          <Timeline
            groups={row3}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableLight}
            axisColor={colors.light}
            xScaleOffset={offset} />
          <Timeline
            groups={row4}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableDeep}
            axisColor={colors.wearableDeep}
            xScaleOffset={offset} />
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
      <svg className="relative top-[10px]" width={width} height={50}>
        <AxisTop
          top={50}
          scale={xScale}
          stroke="transparent"
          tickLength={20}
          tickStroke={colors.light}
          numTicks={window.screen.width > 600 ? 10 : 5}
          tickFormat={v => getTime(v as Date)}
          tickLabelProps={{ angle: -45, dy: -10 }} />
      </svg>
      {visualizations}
    </div>
  );
};


export default WearableVisualizationContent;
