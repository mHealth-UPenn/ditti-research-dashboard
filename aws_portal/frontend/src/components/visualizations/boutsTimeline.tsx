import React, { useMemo } from "react";
import Timeline from "./timeline";
import { IVisualizationProps } from "../../interfaces";

/**
 * A period of time when a subject is considered to be actively tapping
 * start: the start time
 * stop: the stop time
 * rate: the tapping rate during this bout
 */
interface Bout {
  start: number;
  stop?: number;
  label?: string;
}

/**
 * getTaps: get tap data
 * studyDetails: details of the subject's study
 * user: details of the subject
 */
interface BoutsTimelineProps extends IVisualizationProps {
  timestamps: number[];
}

const BoutsTimeline = ({ timestamps, ...props }: BoutsTimelineProps) => {
  console.log(timestamps.length)
  const bouts = useMemo(() => {
    const _bouts: Bout[] = [];
    let first: number;
    let current: number;
    let last: number;
    let group: number[];
    let count = 0;

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
        last = current;
        group.push(current);
        count += 1;
      }

      // If there are 5 taps or more and less than 30 minutes have passed continue the current bout
      else if (count >= 5 && (current - last) < 1800000) {
        last = current;
        group.push(current);
        count += 1;
      }

      // If there are 5 taps or more and 30 minutes or more have passed then the bout ends 10 minutes after the last tap
      else if (count >= 5 && (current - last) >= 1800000) {
        _bouts.push({
          start: first,
          stop: last + 600000,
          label: `${(count / ((last - first) / (600000))).toFixed(1)} taps/min`
        });
        first = current;
        group = [first];
        count = 1;
      }

      // If there are less than 5 taps and more than 10 minutes have passed then append each tap separately
      else if (count < 5 && (current - last) >= 60000) {
        group.forEach(timestamp => _bouts.push({ start: timestamp }));
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
          _bouts.push({ start: timestamp })
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
            label: `${(count / ((current - first) / (600000))).toFixed(1)} taps/min`
          });
        }

        // Else append each tap as a single tap
        else {
          group.forEach(timestamp => _bouts.push({ start: timestamp }));
        }
      }
    });

    return _bouts;
  }, [timestamps]);

  return <Timeline groups={bouts} title="Bouts" hideAxis={true} {...props} />;
};

export default BoutsTimeline;
