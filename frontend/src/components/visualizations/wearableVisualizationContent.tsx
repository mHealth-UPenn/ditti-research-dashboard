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

import { colors } from "../../colors";
import { useVisualization } from "../../hooks/useVisualization";
import { useWearableData } from "../../hooks/useWearableData";
import { Timeline } from "./timeline";
import { AxisTop } from "@visx/axis";
import { GridColumns } from "@visx/grid";
import { Brush } from "@visx/brush";
import { scaleLinear } from "@visx/scale";
import { Button } from "../buttons/button";
import ReplayIcon from "@mui/icons-material/Replay";
import { differenceInDays } from "date-fns";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import { useEffect, useMemo, useState } from "react";
import { useDittiData } from "../../hooks/useDittiData";
import { BoutsTimeline } from "./boutsTimeline";
import { SmallLoader } from "../loader/loader";
import {
  WearableVisualizationContentProps,
  Group,
  LevelGroupsStages,
  LevelGroupsClassic,
} from "./visualizations.types";
import { SleepLevelClassic, SleepLevelStages } from "../../types/api";

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
  return date.toLocaleTimeString("en-US", {
    hour12: true,
    hour: "numeric",
    minute: "numeric",
  });
};

export const WearableVisualizationContent = ({
  marginTop,
  marginRight,
  marginBottom,
  marginLeft,
  showDayControls = false,
  showTapsData = false,
  dittiId,
  horizontalPadding = false,
}: WearableVisualizationContentProps) => {
  // Sleep logs may straddle multiple timeline windows, so initialize one array
  // for each sleep stage that will contain data from all sleep logs
  const [row1, setRow1] = useState<Group[]>([]); // awake
  const [row2, setRow2] = useState<Group[]>([]); // rem (if available)
  const [row3, setRow3] = useState<Group[]>([]); // light or restless
  const [row4, setRow4] = useState<Group[]>([]); // deep or asleep

  const { width, xScale, defaultMargin, onZoomChange, resetZoom } =
    useVisualization();

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
  const timestamps = useMemo(
    () =>
      taps
        .filter((tap) => tap.dittiId === dittiId)
        .map((tap) => tap.time.getTime()),
    [taps, dittiId]
  );

  const audioTimestamps = useMemo(
    () =>
      audioTaps
        .filter((tap) => tap.dittiId === dittiId)
        .map((tap) => tap.time.getTime()),
    [audioTaps, dittiId]
  );

  // Optionally override the default margins if passed as props
  const margin = {
    top: marginTop ?? defaultMargin.top,
    right: marginRight ?? defaultMargin.right,
    bottom: marginBottom ?? defaultMargin.bottom,
    left: marginLeft ?? defaultMargin.left,
  };

  // Generate the row visualizations on load and when data changes.
  useEffect(() => {
    if (isLoading) {
      return;
    }

    const updatedRow1: Group[] = [];
    const updatedRow2: Group[] = [];
    const updatedRow3: Group[] = [];
    const updatedRow4: Group[] = [];

    // If data is being updated, only get new data that is not currently being visualized (any data that appears before
    // the earliest sleep log)
    let filteredSleepLogs = [...sleepLogs];
    if (dataIsUpdated && firstDateOfSleep) {
      filteredSleepLogs = filteredSleepLogs.filter(
        (sl) => new Date(sl.dateOfSleep) <= firstDateOfSleep
      );
    }

    filteredSleepLogs.forEach((sl) => {
      // Create groups for stages data
      if (sl.type === "stages") {
        const levelGroups: LevelGroupsStages = {
          wake: [],
          rem: [],
          light: [],
          deep: [],
        };

        sl.levels.forEach((l) => {
          const dateTime = new Date(l.dateTime);

          levelGroups[l.level as SleepLevelStages].push({
            start: dateTime.getTime(),
            stop: dateTime.getTime() + l.seconds * 1000,
            strokeDashArray: "",
          });
        });

        // Insert new data to the beginning of data to be visualized
        updatedRow1.push(...levelGroups.wake);
        updatedRow2.push(...levelGroups.rem);
        updatedRow3.push(...levelGroups.light);
        updatedRow4.push(...levelGroups.deep);
      }

      // Else create groups for classic data
      else {
        const levelGroups: LevelGroupsClassic = {
          awake: [],
          restless: [],
          asleep: [],
        };

        sl.levels.forEach((l) => {
          const dateTime = new Date(l.dateTime);

          levelGroups[l.level as SleepLevelClassic].push({
            start: dateTime.getTime(),
            stop: dateTime.getTime() + l.seconds * 1000,
            strokeDashArray: "1,1",
          });
        });

        // Insert new data to the beginning of data to be visualized
        updatedRow1.push(...levelGroups.awake);
        updatedRow3.push(...levelGroups.restless);
        updatedRow4.push(...levelGroups.asleep);
      }
    });

    // Append existing data to the end of data to be visualized
    setRow1((prev) => [...prev, ...updatedRow1]);
    setRow2((prev) => [...prev, ...updatedRow2]);
    setRow3((prev) => [...prev, ...updatedRow3]);
    setRow4((prev) => [...prev, ...updatedRow4]);
  }, [dataIsUpdated, firstDateOfSleep, isLoading, sleepLogs]);

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
  for (
    let day = new Date(startDate);
    day < endDate;
    day.setDate(day.getDate() + 1)
  ) {
    const title = getWeekday(day);

    // Calculate the offset from today to the day to visualize in milliseconds
    const offset =
      (differenceInDays(day, new Date()) + 1) * 24 * 60 * 60 * 1000;

    visualizations.push(
      <div
        key={day.toISOString()}
        className="relative mb-10 flex items-center md:mb-8"
      >
        {/* The weekday label to display to the left on large screens */}
        <span
          className="absolute hidden rotate-180 text-sm font-bold
            [writing-mode:vertical-lr] md:flex"
        >
          {title}
        </span>
        <div>
          {/* Vertical grid lines for all timelines in this day */}
          <svg className="absolute" width={width} height={80}>
            <GridColumns
              scale={xScale}
              width={width - margin.left - margin.right}
              height={80 - margin.bottom - margin.top}
              stroke={colors.light}
              strokeDasharray="5,5"
              numTicks={window.screen.width > 600 ? 10 : 5}
            />
          </svg>

          {/* The weekday label to display on top on small screens */}
          <span className="absolute top-[-28px] text-sm font-bold md:hidden">
            {title}
          </span>

          {/* Timelines for all four levels (wake, rem, light, deep) */}
          <Timeline
            groups={row1}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableWake}
            axisColor={colors.light}
            xScaleOffset={offset}
          />
          <Timeline
            groups={row2}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableRem}
            axisColor={colors.light}
            xScaleOffset={offset}
          />
          <Timeline
            groups={row3}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableLight}
            axisColor={colors.light}
            xScaleOffset={offset}
          />
          <Timeline
            groups={row4}
            hideAxis={true}
            hideTicks={true}
            hideStops={true}
            strokeWidth={16}
            color={colors.wearableDeep}
            axisColor={colors.wearableDeep}
            xScaleOffset={offset}
          />

          {/* Taps data to display, if any */}
          {showTapsData && (
            <>
              <div className="mb-4" />
              <BoutsTimeline
                timestamps={timestamps}
                audioTimestamps={audioTimestamps}
                hideTicks={true}
                xScaleOffset={offset}
                title=""
              />
            </>
          )}

          {/* Brush for clicking and dragging to zoom */}
          <svg className="absolute top-0" width={width} height={80}>
            <Brush
              xScale={xScale}
              yScale={scaleLinear({ domain: [0, 80], range: [0, 80] })}
              width={width}
              height={80 - margin.bottom - margin.top}
              onBrushEnd={(bounds) => {
                if (bounds) {
                  onZoomChange([bounds.x0, bounds.x1]);
                }
              }}
              resetOnEnd={true}
            />
          </svg>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <div
        className="mb-2 flex flex-col-reverse justify-center sm:flex-row
          sm:items-center sm:justify-between"
      >
        <div className="flex flex-col">
          {/* Stages data legend */}
          <div className="mb-1 flex">
            <span className="w-12 text-xs font-bold">Stages:</span>
            <div className="mr-4 flex">
              <div className="mr-2 w-4 bg-wearable-wake" />
              <span className="text-xs">Awake</span>
            </div>
            <div className="mr-4 flex">
              <div className="mr-2 w-4 bg-wearable-rem" />
              <span className="text-xs">REM</span>
            </div>
            <div className="mr-4 flex">
              <div className="mr-2 w-4 bg-wearable-light" />
              <span className="text-xs">Light</span>
            </div>
            <div className="flex">
              <div className="mr-2 w-4 bg-wearable-deep" />
              <span className="text-xs">Deep</span>
            </div>
          </div>

          {/* Classic data legend */}
          <div className="mb-1 flex">
            <span className="w-12 text-xs font-bold">Classic:</span>
            <div className="mr-4 flex">
              <div
                className="mr-2 w-4
                  bg-[repeating-linear-gradient(90deg,#E04B6F,#E04B6F_1px,transparent_1px,transparent_2px)]"
              />
              <span className="text-xs">Awake</span>
            </div>
            <div className="mr-4 flex">
              <div
                className="mr-2 w-4
                  bg-[repeating-linear-gradient(90deg,#5489F5,#5489F5_1px,transparent_1px,transparent_2px)]"
              />
              <span className="text-xs">Restless</span>
            </div>
            <div className="flex">
              <div
                className="mr-2 w-4
                  bg-[repeating-linear-gradient(90deg,#24499F,#24499F_1px,transparent_1px,transparent_2px)]"
              />
              <span className="text-xs">Asleep</span>
            </div>
          </div>

          {/* Taps data legend */}
          {showTapsData && (
            <div className="flex">
              <span className="w-12 text-xs font-bold">Taps:</span>
              <div className="mr-4 flex items-center">
                <div className="mr-2 size-[0.6rem] rounded-lg bg-secondary" />
                <span className="text-xs">Tap</span>
              </div>
              <div className="mr-4 flex items-center">
                <div className="relative flex items-center">
                  <div className="mr-2 size-[0.6rem] rounded-lg bg-secondary" />
                  <div className="mr-2 size-[0.6rem] rounded-lg bg-secondary" />
                  <div className="absolute h-[2px] w-5 bg-secondary" />
                </div>
                <span className="text-xs">Tapping Bout</span>
              </div>
              <div className="mr-4 flex items-center">
                <div className="mr-2 size-[0.6rem] rounded-lg bg-light" />
                <span className="text-xs">Audio Tap</span>
              </div>
            </div>
          )}
        </div>
        <div className="mb-4 flex flex-col items-end sm:mb-0">
          <div className="flex">
            {/* Controls for changing the visualization start date, if shown */}
            {showDayControls && (
              <>
                <Button
                  square={true}
                  size="sm"
                  variant="tertiary"
                  className="rounded-l"
                  onClick={decrementStartDate}
                >
                  <KeyboardArrowUp />
                </Button>
                <Button
                  square={true}
                  size="sm"
                  variant="tertiary"
                  className="mr-2 rounded-r border-l-0"
                  onClick={incrementStartDate}
                  disabled={!canIncrementStartDate}
                >
                  <KeyboardArrowDown />
                </Button>
              </>
            )}

            {/* Button for resetting visualization */}
            <Button
              square={true}
              size="sm"
              variant="primary"
              onClick={resetVisualization}
              rounded={true}
            >
              <ReplayIcon />
            </Button>
          </div>
          <div>
            <span className="text-sm italic">Click and drag to zoom</span>
          </div>
        </div>
      </div>

      {/* Time ticks at the top of the visualization */}
      <svg
        className="relative top-[10px]"
        width={width}
        height={horizontalPadding ? 50 : 90}
      >
        <AxisTop
          top={50}
          scale={xScale}
          stroke="transparent"
          tickLength={20}
          tickStroke={colors.light}
          numTicks={window.screen.width > 600 ? 10 : 5}
          tickValues={
            horizontalPadding
              ? xScale.ticks()
              : xScale.ticks().slice(1, xScale.ticks().length - 1)
          }
          tickFormat={(v) => getTime(v as Date)}
          tickLabelProps={{ angle: -45, dy: -10 }}
        />
      </svg>

      {visualizations}
    </div>
  );
};
