import { useMemo } from "react";
import { Timeline } from "./timeline";
import { IVisualizationProps } from "../../interfaces";
import { colors } from "../../colors";

/**
 * A period of time when a subject is considered to be actively tapping
 * @property start: the start time
 * @property stop: the stop time
 * @property label: the tapping rate during this bout
 * @property color: an optional color to display on the timeline
 */
interface Bout {
  start: number;
  stop?: number;
  label?: string;
  color?: string;
}

// TODO: Extend a new "ITimelineProps"
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
interface BoutsTimelineProps extends IVisualizationProps {
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

export const BoutsTimeline = ({
  timestamps,
  audioTimestamps,
  title = "Bouts",
  hideAxis = true,
  ...props
}: BoutsTimelineProps) => {

  // Memoize the bouts calculation
  const bouts = useMemo(() => {
    const _bouts: Bout[] = [];

    // The current group of timestamps
    let group: number[];
    
    // The number of timestamps in the current group
    let count = 0;

    // The first timestamp in the current group of timestamps
    let first: number;

    // The current timestamp
    let current: number;

    // The previous timestamp
    let previous: number;

    timestamps.sort().forEach((timestamp, i) => {
      // On first iteration
      if (!count) {
        first = timestamp;
        group = [first];
        count = 1;
        return;
      }

      current = timestamp;

      // If this tap is less than one minute after the first tap then continue the current bout
      if (current - first < 60000) {
        previous = current;
        group.push(current);
        count += 1;
      }

      // If there are 5 taps or more and less than 30 minutes have passed continue the current bout
      else if (count >= 5 && (current - previous) < 1800000) {
        previous = current;
        group.push(current);
        count += 1;
      }

      // If there are 5 taps or more and 30 minutes or more have passed then the bout ends 10 minutes after the previous tap
      else if (count >= 5 && (current - previous) >= 1800000) {
        _bouts.push({
          start: first,
          stop: previous + 600000,
          label: `${(count / ((previous - first) / (600000))).toFixed(1)} taps/min`,
          color: colors.secondary,
        });
        first = current;
        group = [first];
        count = 1;
      }

      // If there are less than 5 taps and more than 10 minutes have passed then append each tap separately
      else if (count < 5 && (current - previous) >= 60000) {
        group.forEach(timestamp => _bouts.push({
          start: timestamp,
          color: colors.secondary,
        }));
        first = current;
        group = [first];
        count = 1;
      }

      // Otherwise append all taps that are one minute or more before the current tap separately
      else {
        // Get the index of the first timestamp within one minute of the current time
        const idx = group.findIndex(timestamp => current - timestamp < 60000);

        // Append each preceding timestamp as a single tap
        group.slice(0, idx).forEach(timestamp =>
          _bouts.push({ start: timestamp, color: colors.secondary })
        );

        // Use the remaining timestamps within one minute of the current time to try and start another bout
        group = group.slice(idx);

        if (group.length) {
          // Append each tap as a single tap, no bout
          first = group[0];
          count = group.length;
        } else {
          first = current;
          group = [first];
          count = 1;
        }
      }

      // If on the last iteration
      if (i === timestamps.length - 1) {
        // If a valid bout
        if (count >= 5 && (current - first) >= 600000) {
          _bouts.push({
            start: first,
            stop: current + 600000,
            label: `${(count / ((current - first) / (600000))).toFixed(1)} taps/min`,
            color: colors.secondary,
          });
        }

        // Else append each tap as a single tap
        else {
          group.forEach(timestamp => _bouts.push({
            start: timestamp,
            color: colors.secondary
          }));
        }

        // Append any audio taps separately
        if (audioTimestamps) {
          audioTimestamps.forEach(timestamp =>
            _bouts.push({ start: timestamp, color: colors.secondaryLight })
          );
        }
      }
    });

    return _bouts;
  }, [timestamps]);

  return <Timeline
    groups={bouts} title={title} hideAxis={hideAxis} {...props} />;
};
