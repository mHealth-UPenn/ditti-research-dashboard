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
export interface Group { start: number; stop: number; strokeDashArray: string; }

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
export type TimelineGroup = {
  start: number;
  stop?: number;
  label?: string;
  strokeDashArray?: string;
  color?: string;
};

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
