import { Timeline } from "./timeline";
import { AudioTapsTimelineProps } from "./visualizations.types";

export const AudioTapsTimeline = ({
  audioTaps,
  ...props
}: AudioTapsTimelineProps) => {
  const groups = audioTaps.map((at) => ({
    start: at.time.getTime(),
    label: at.action,
  }));

  return <Timeline groups={groups} title="Audio" hideAxis={true} {...props} />;
};
