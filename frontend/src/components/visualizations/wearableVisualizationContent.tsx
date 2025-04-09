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

import { colors } from "../../colors";
import { useVisualizationContext } from "../../contexts/visualizationContext";
import { useWearableData } from "../../contexts/wearableDataContext";
import { ISleepLevelClassic, ISleepLevelStages, IVisualizationProps } from "../../interfaces";
import { Timeline } from "./timeline";
import { AxisTop } from "@visx/axis";
import { GridColumns } from '@visx/grid';
import { Brush } from '@visx/brush';
import { scaleLinear } from '@visx/scale';
import { Button } from "../buttons/button";
import ReplayIcon from '@mui/icons-material/Replay';
import { differenceInDays } from "date-fns";
import { KeyboardArrowDown } from "@mui/icons-material";
import { KeyboardArrowUp } from "@mui/icons-material";
import { useEffect, useMemo, useState } from "react";
import { useDittiData } from "../../hooks/useDittiData";
import { BoutsTimeline } from "./boutsTimeline";
import { SmallLoader } from "../loader";


/**
 * Get the weekday of a date.
 * @param date: The date to get the weekday of.
 * @returns string - The weekday string.
 */
const getWeekday = (date: Date): string => {
  return date.toLocaleDateString("en-US", { weekday: "long" });
};


/**
 * Get the time of a date in 12-hour H:MM format.
 * @param date: The date to get the time of.
 * @returns string - The formatted time.
 */
const getTime = (date: Date) => {
  return date.toLocaleTimeString(
    "en-US", { hour12: true, hour: "numeric", minute: "numeric" }
  );
}

// Interface for sleep level ranges to display
interface IGroup { start: number; stop: number; strokeDashArray: string; }

// Sleep level data for stages data
type ILevelGroupsStages = Record<ISleepLevelStages, IGroup[]>;

// Sleep level data for classic data
type ILevelGroupsClassic = Record<ISleepLevelClassic, IGroup[]>;


/**
 * Props for the wearable visualization.
 * @property showDayControls: Whether to show buttons for controlling the start date of the visualization.
 * @property showTapsData: Whether to show taps data with wearable data.
 * @property dittiId: The Ditti ID of the participant whose data is being visualized.
 * @property horizontalPadding: Whether horizontal padding is added to the visualization. If it is not, then hide the
 *   first and last x axis ticks and add extra padding on top of each weekday visualization to make space for a label.
 */
interface IWearableVisualizationContentProps extends IVisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  dittiId?: string;
  horizontalPadding?: boolean;
}


export const WearableVisualizationContent = ({
  marginTop,
  marginRight,
  marginBottom,
  marginLeft,
  showDayControls = false,
  showTapsData = false,
  dittiId,
  horizontalPadding = false,
}: IWearableVisualizationContentProps) => {

  // Sleep logs may straddle multiple timeline windows, so initialize one array
  // for each sleep stage that will contain data from all sleep logs
  const [row1, setRow1] = useState<IGroup[]>([]);  // awake
  const [row2, setRow2] = useState<IGroup[]>([]);  // rem (if available)
  const [row3, setRow3] = useState<IGroup[]>([]);  // light or restless
  const [row4, setRow4] = useState<IGroup[]>([]);  // deep or asleep

  const {
    width,
    xScale,
    defaultMargin,
    onZoomChange,
    resetZoom
  } = useVisualizationContext();

  const {
    startDate,
    endDate,
    sleepLogs,
    isLoading,
    firstDateOfSleep,
    dataIsUpdated,
    canIncrementStartDate,
    decrementStartDate,
    incrementStartDate,
    resetStartDate,
  } = useWearableData();

  const { dataLoading, taps, audioTaps } = useDittiData();

  // Get only the taps and audio taps that belong to the current participant.
  const timestamps = useMemo(() => taps
      .filter(tap => tap.dittiId === dittiId)
      .map(tap => tap.time.getTime())
  , [taps]);

  const audioTimestamps = useMemo(() => audioTaps
      .filter(tap => tap.dittiId === dittiId)
      .map(tap => tap.time.getTime())
  , [taps]);

  // Optionally override the default margins if passed as props
  const margin = {
    top: marginTop !== undefined ? marginTop : defaultMargin.top,
    right: marginRight !== undefined ? marginRight : defaultMargin.right,
    bottom: marginBottom !== undefined ? marginBottom : defaultMargin.bottom,
    left: marginLeft !== undefined ? marginLeft : defaultMargin.left,
  }

  // Generate the row visualizations on load and when data changes.
  useEffect(() => {
    if (isLoading) {
      return;
    }

    const updatedRow1 = [];
    const updatedRow2 = [];
    const updatedRow3 = [];
    const updatedRow4 = [];

    // If data is being updated, only get new data that is not currently being visualized (any data that appears before
    // the earliest sleep log)
    let filteredSleepLogs = [...sleepLogs];
    if (dataIsUpdated && firstDateOfSleep) {
      filteredSleepLogs = filteredSleepLogs.filter(sl =>
        new Date(sl.dateOfSleep) <= firstDateOfSleep
      );
    }

    filteredSleepLogs.forEach(sl => {
      // Create groups for stages data
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

        // Insert new data to the beginning of data to be visualized
        updatedRow1.push(...levelGroups.wake);
        updatedRow2.push(...levelGroups.rem);
        updatedRow3.push(...levelGroups.light);
        updatedRow4.push(...levelGroups.deep);
      }

      // Else create groups for classic data
      else {
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

        // Insert new data to the beginning of data to be visualized
        updatedRow1.push(...levelGroups.awake);
        updatedRow3.push(...levelGroups.restless);
        updatedRow4.push(...levelGroups.asleep);
      }
    });

    // Append existing data to the end of data to be visualized
    updatedRow1.push(...row1);
    updatedRow2.push(...row2);
    updatedRow3.push(...row3);
    updatedRow4.push(...row4);

    setRow1(updatedRow1);
    setRow2(updatedRow2);
    setRow3(updatedRow3);
    setRow4(updatedRow4);
  }, [dataIsUpdated, firstDateOfSleep, isLoading]);

  // Reset the zoom and start date
  const resetVisualization = () => {
    resetZoom();
    if (resetStartDate) {
      resetStartDate();
    }
  };

  if (isLoading || !xScale || dataLoading) {
    return <SmallLoader />;
  }

  // Iterate through each day currently being visualized
  const visualizations: React.ReactElement[] = [];
  for (let day = new Date(startDate); day < endDate; day.setDate(day.getDate() + 1)) {
    const title = getWeekday(day);

    // Calculate the offset from today to the day to visualize in milliseconds
    const offset = (differenceInDays(day, new Date()) + 1) * 24 * 60 * 60 * 1000;

    visualizations.push(
      <div key={day.toISOString()} className="relative flex items-center mb-10 md:mb-8">

        {/* The weekday label to display to the left on large screens */}
        <span className="absolute hidden md:flex font-bold text-sm [writing-mode:vertical-lr] rotate-180">{title}</span>
        <div>

          {/* Vertical grid lines for all timelines in this day */}
          <svg className="absolute" width={width} height={80}>
            <GridColumns
              scale={xScale}
              width={width - margin.left - margin.right}
              height={80 - margin.bottom - margin.top}
              stroke={colors.light}
              strokeDasharray="5,5"
              numTicks={window.screen.width > 600 ? 10 : 5} />
          </svg>

          {/* The weekday label to display on top on small screens */}
          <span className="md:hidden absolute font-bold text-sm top-[-28px]">{title}</span>

          {/* Timelines for all four levels (wake, rem, light, deep) */}
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

          {/* Taps data to display, if any */}
          {showTapsData &&
            <>
              <div className="mb-4" />
              <BoutsTimeline
                timestamps={timestamps}
                audioTimestamps={audioTimestamps}
                hideTicks={true}
                xScaleOffset={offset}
                title="" />
            </>
          }

          {/* Brush for clicking and dragging to zoom */}
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
    )
  }

  return (
    <div className="flex flex-col">
      <div className="flex flex-col-reverse justify-center sm:flex-row sm:items-center sm:justify-between mb-2">
        <div className="flex flex-col">

          {/* Stages data legend */}
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

          {/* Classic data legend */}
          <div className="flex mb-1">
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

          {/* Taps data legend */}
          {showTapsData &&
            <div className="flex">
              <span className="text-xs font-bold w-[3rem]">Taps:</span>
              <div className="flex items-center mr-4">
                <div className="bg-secondary w-[0.6rem] h-[0.6rem] mr-2 rounded-lg" />
                <span className="text-xs">Tap</span>
              </div>
              <div className="flex items-center mr-4">
                <div className="relative flex items-center">
                  <div className="bg-secondary w-[0.6rem] h-[0.6rem] mr-2 rounded-lg" />
                  <div className="bg-secondary w-[0.6rem] h-[0.6rem] mr-2 rounded-lg" />
                  <div className="absolute h-[2px] w-[1.25rem] bg-secondary" />
                </div>
                <span className="text-xs">Tapping Bout</span>
              </div>
              <div className="flex items-center mr-4">
                <div className="bg-light w-[0.6rem] h-[0.6rem] mr-2 rounded-lg" />
                <span className="text-xs">Audio Tap</span>
              </div>
            </div>
          }
        </div>
        <div className="flex flex-col items-end mb-4 sm:mb-0">
          <div className="flex">

            {/* Controls for changing the visualization start date, if shown */}
            {showDayControls &&
              <>
                <Button
                  square={true}
                  size="sm"
                  variant="tertiary"
                  className="rounded-l-[0.25rem]"
                  onClick={decrementStartDate}>
                    <KeyboardArrowUp />
                </Button>
                <Button
                  square={true}
                  size="sm"
                  variant="tertiary"
                  className="mr-2 border-l-0 rounded-r-[0.25rem]"
                  onClick={incrementStartDate}
                  disabled={!canIncrementStartDate}>
                    <KeyboardArrowDown />
                </Button>
              </>
            }

            {/* Button for resetting visualization */}
            <Button
              square={true}
              size="sm"
              variant="primary"
              onClick={resetVisualization}
              rounded={true}>
                <ReplayIcon />
            </Button>
          </div>
          <div>
            <span className="italic text-sm">Click and drag to zoom</span>
          </div>
        </div>
      </div>

      {/* Time ticks at the top of the visualization */}
      <svg className="relative top-[10px]" width={width} height={horizontalPadding ? 50 : 90}>
        <AxisTop
          top={50}
          scale={xScale}
          stroke="transparent"
          tickLength={20}
          tickStroke={colors.light}
          numTicks={window.screen.width > 600 ? 10 : 5}
          tickValues={horizontalPadding ? xScale.ticks() : xScale.ticks().slice(1, xScale.ticks().length - 1)}
          tickFormat={v => getTime(v as Date)}
          tickLabelProps={{ angle: -45, dy: -10 }} />
      </svg>

      {visualizations}
    </div>
  );
};
