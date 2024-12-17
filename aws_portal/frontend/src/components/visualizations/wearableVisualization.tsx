import VisualizationController from "./visualizationController";
import WearableVisualizationContent from "./wearableVisualizationContent";

interface IWearableVisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  horizontalPadding?: boolean;
}


const WearableVisualization = ({
  showDayControls = false,
  showTapsData = false,
  horizontalPadding = false,
}: IWearableVisualizationProps) => {
  return (
    <VisualizationController
      defaultMargin={{
        top: 8,
        right: horizontalPadding ? 30 : 2,
        bottom: 8,
        left: horizontalPadding ? 40 : 2
      }}>
        <WearableVisualizationContent
          showDayControls={showDayControls}
          showTapsData={showTapsData}
          horizontalPadding={horizontalPadding} />
    </VisualizationController>
  );
};


export default WearableVisualization;
