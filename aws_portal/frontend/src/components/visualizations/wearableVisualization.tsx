import VisualizationController from "./visualizationController";
import WearableVisualizationContent from "./wearableVisualizationContent";

interface IWearableVisualizationProps {
  showDayControls?: boolean;
  horizontalPadding?: boolean;
}


const WearableVisualization = ({
  showDayControls = false,
  horizontalPadding = false,
}: IWearableVisualizationProps) => {
  return (
    <VisualizationController
      defaultMargin={{ top: 8, right: horizontalPadding ? 30 : 2, bottom: 8, left: horizontalPadding ? 40 : 2 }}>
      {/* defaultMargin={{ top: 8, right: 30, bottom: 8, left: 40 }}> */}
        <WearableVisualizationContent
          showDayControls={showDayControls}
          horizontalPadding={horizontalPadding} />
    </VisualizationController>
  );
};


export default WearableVisualization;
