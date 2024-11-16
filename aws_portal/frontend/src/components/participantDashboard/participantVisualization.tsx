import { useWearableData } from "../../contexts/wearableDataContext";


const ParticipantVisualization = () => {
  const { sleepLogs } = useWearableData();

  return (
    <div>Visualization</div>
  );
};


export default ParticipantVisualization;
