import { useWearableData } from "../../contexts/wearableDataContext";
import Timeline from "../visualizations/timeline";
import VisualizationController from "../visualizations/visualizationController";


const getWeekday = (date: Date) => {
  return date.toLocaleDateString("en-US", { weekday: "long" });
};


const ParticipantVisualization = () => {
  const { sleepLogs, isLoading } = useWearableData();

  let groups: { start: number; stop: number; }[] = [];
  let title = "";
  if (!isLoading) {
    groups = sleepLogs[sleepLogs.length - 1].levels.map(l => ({
      start: l.dateTime.getTime(),
      stop: l.dateTime.getTime() + l.seconds * 1000,
    }))
    title = getWeekday(sleepLogs[sleepLogs.length - 1].dateOfSleep);
  }

  return (
    <VisualizationController>
      <Timeline
        groups={groups}
        title={title} />
    </VisualizationController>
  );
};


export default ParticipantVisualization;
