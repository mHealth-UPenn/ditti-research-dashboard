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

import { SleepLevelStages, SleepLevelClassic } from "../../types/api";
import { AudioTapModel } from "../../types/models";

/**
 * Default props to pass to any visualization component.
 * @property marginTop - The default margin at the top of the visualization.
 * @property marginRight - The default margin at the right of the visualization.
 * @property marginBottom - The default margin at the bottom of the visualization.
 * @property marginLeft - The default margin at the left of the visualization.
 */
export interface VisualizationProps {
  marginTop?: number;
  marginRight?: number;
  marginBottom?: number;
  marginLeft?: number;
}

// Interface for sleep level ranges to display
export interface Group {
  start: number;
  stop: number;
  strokeDashArray: string;
}

// Sleep level data for stages data
export type LevelGroupsStages = Record<SleepLevelStages, Group[]>;

// Sleep level data for classic data
export type LevelGroupsClassic = Record<SleepLevelClassic, Group[]>;

/**
 * Props for the wearable visualization.
 * @property showDayControls: Whether to show buttons for controlling the start date of the visualization.
 * @property showTapsData: Whether to show taps data with wearable data.
 * @property dittiId: The Ditti ID of the participant whose data is being visualized.
 * @property horizontalPadding: Whether horizontal padding is added to the visualization. If it is not, then hide the
 *   first and last x axis ticks and add extra padding on top of each weekday visualization to make space for a label.
 */
export interface WearableVisualizationContentProps extends VisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  dittiId?: string;
  horizontalPadding?: boolean;
}

/**
 * Props to pass to the wearable visualization.
@ @property showDayControls: `showDayControls` to pass to `WearableVisualizationContent`.
@ @property showTapsData: `showTapsData` to pass to `WearableVisualizationContent`.
@ @property dittiId: `dittiId` to pass to `WearableVisualizationContent`.
@ @property horizontalPadding: Whether to add horizontal padding to the visualization.
 */
export interface WearableVisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  dittiId?: string;
  horizontalPadding?: boolean;
}

/**
 * Props for the timestamp histogram.
 * @property: Timestamps for each tap to visualize.
 * @property: Timezones in the tapping data, where `time` is the first timestamp in the timezone called `name`.
 */
export interface TimestampHistogramProps extends VisualizationProps {
  timestamps: number[];
  timezones?: { time: number; name: string }[];
}

/**
 * Either a single point or range on the timeline.
 * @property start: A timestamp representing a single point or the start of a range.
 * @property stop: An optional timestamp representing the end of a range.
 * @property label: An optional label to display on hover.
 * @property strokeDashArray: An optional stroke dash array to pas to `Line`.
 * @property color: An optional color to display the point or range as.
 */
export interface TimelineGroup {
  start: number;
  stop?: number;
  label?: string;
  strokeDashArray?: string;
  color?: string;
}

/**
 * Props for the `Timeline` visualization.
 * @property groups: An array of `TimelineGroup` representing points or ranges to display on the timeline.
 * @property title: A title. Titles are displayed to the left of the timeline and rotated 90 degrees.
 * @property hideAxis: Whether to hide the axis.
 * @property hideStops: Whether to hide start and stop points on ranges.
 * @property hideTicks: Whether to hide ticks on the timeline.
 * @property xScaleOffset: The number of milliseconds to offset data by.
 * @property strokeWidth: The stroke height of ranges.
 * @property color: The default color for points and ranges. This is overridden by any `color` property passed in
 *   `groups`.
 * @property axisColor: The axis color.
 * @property strokeDashArray: The default stroke dash array for ranges. This is overridden by any `strokeDashArray`
 *   property passed in `groups`.
 */
export interface TimelineProps extends VisualizationProps {
  groups: TimelineGroup[];
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

/**
 * A period of time when a subject is considered to be actively tapping
 * @property start: the start time
 * @property stop: the stop time
 * @property label: the tapping rate during this bout
 * @property color: an optional color to display on the timeline
 */
export interface Bout {
  start: number;
  stop?: number;
  label?: string;
  color?: string;
}

/**
 * @property timestamps: Timestamps of all tapping data to display
 * @property audioTimestamps: Timestamps of audio taps to optionally display
 * @property title: `title` to pass to `Timeline`
 * @property hideAxis: `hideAxis` to pass to `Timeline`
 * @property hideStops: `hideStops` to pass to `Timeline`
 * @property hideTicks: `hideTicks` to pass to `Timeline`
 * @property xScaleOffset: `xScaleOffset` to pass to `Timeline`
 * @property strokeWidth: `strokeWidth` to pass to `Timeline`
 * @property color: `color` to pass to `Timeline`
 * @property axisColor: `axisColor` to pass to `Timeline`
 * @property strokeDashArray: `strokeDashArray` to pass to `Timeline`
 */
export interface BoutsTimelineProps extends VisualizationProps {
  timestamps: number[];
  audioTimestamps?: number[];
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

/**
 * Props for the audio taps timeline.
 * @property audioTaps: The audio taps to display.
 */
export interface AudioTapsTimelineProps extends VisualizationProps {
  audioTaps: AudioTapModel[];
}
