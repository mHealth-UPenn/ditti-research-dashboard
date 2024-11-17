import { AudioTapDetails } from "../../interfaces";
import Timeline from "./timeline";

interface AudioTapsTimelineProps {
  audioTaps: AudioTapDetails[];
}


const AudioTapsTimeline = ({ audioTaps }: AudioTapsTimelineProps) => {
  const groups = audioTaps.map(at => ({
    start: at.time.getTime(),
    label: at.action,
  }));

  return <Timeline groups={groups} title="Audio" hideAxis={true} />
};


export default AudioTapsTimeline;
