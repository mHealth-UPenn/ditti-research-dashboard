import React, { useMemo, useState } from "react";
import Timeline from "./timeline";

/**
 * A period of time when a subject is considered to be actively tapping
 * start: the start time
 * stop: the stop time
 * rate: the tapping rate during this bout
 */
interface Bout {
  start: number;
  stop: number;
  label: string;
}

/**
 * getTaps: get tap data
 * studyDetails: details of the subject's study
 * user: details of the subject
 */
interface BoutsTimelineProps {
  timestamps: number[];
}

const BoutsTimeline: React.FC<BoutsTimelineProps> = ({ timestamps }) => {
  const bouts = useMemo(() => {
    const _bouts: Bout[] = [];
    let first: number;
    let current: number;
    let last: number;
    let group: number[];
    let count = 0;

    timestamps.forEach((timestamp) => {

      // on first iteration
      if (!count) {
        first = timestamp;
        group = [first];
        count = 1;
        return;
      }

      current = timestamp;

      // if this tap is less than one minute after the first tap
      if (current - first < 60000) {
        last = current;
        group.push(current);
        count += 1;
      }

      // else if there were 5 taps or more in the first minute and less than 30
      // minutes have passed between this tap and the last tap then the bout
      // begins at the first tap
      else if (count >= 5 && (current - last) < 1800000) {
        last = current;
        group.push(current);
        count += 1;
      }

      // else if there were 5 taps or more in the first minute and more than 10
      // minutes have passed then the bout ends at 10 minutes after the last
      // tap
      else if (count >= 5 && (last - first) > 60000) {
        bouts.push({
          start: first,
          stop: last + 1800000,
          label: `${count / (last - first) / (60 * 60 * 1000)} taps/min`
        });
        first = current;
        group = [first];
        count = 1;
      }

      // else if there were less than 5 taps in the first minute or tapping
      // lasted for less than one minute then no bout has begun
      else {
        group = group.filter(timestamp => current - timestamp < 60000);
        if (group.length) {
          first = group[0];
          count = group.length;
        } else {
          first = current;
          group = [first];
          count = 1;
        }
      }
    });

    return _bouts;
  }, [timestamps]);

  return (
    <></>
  );
};

export default BoutsTimeline;
