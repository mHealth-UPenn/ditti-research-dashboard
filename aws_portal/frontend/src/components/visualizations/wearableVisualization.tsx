import VisualizationController from "./visualizationController";
import WearableVisualizationContent from "./wearableVisualizationContent";

interface IWearableVisualizationProps {
  showDayControls?: boolean;
}


const WearableVisualization = ({
  showDayControls = false,
}: IWearableVisualizationProps) => {
  return (
    <VisualizationController
      defaultMargin={{ top: 8, right: 30, bottom: 8, left: 40 }}>
        <WearableVisualizationContent showDayControls={showDayControls} />
    </VisualizationController>
  );
};


export default WearableVisualization;
