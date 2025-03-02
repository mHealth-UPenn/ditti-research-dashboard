import { AudioTapDetails, IVisualizationProps } from "../../interfaces";
import { Timeline } from "./timeline";

interface AudioTapsTimelineProps extends IVisualizationProps {
  audioTaps: AudioTapDetails[];
}


export const AudioTapsTimeline = ({ audioTaps, ...props }: AudioTapsTimelineProps) => {
  const groups = audioTaps.map(at => ({
    start: at.time.getTime(),
    label: at.action,
  }));

  return <Timeline groups={groups} title="Audio" hideAxis={true} {...props} />
};
