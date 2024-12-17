import VisualizationController from "./visualizationController";
import WearableVisualizationContent from "./wearableVisualizationContent";

interface IWearableVisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  dittiId?: string;
  horizontalPadding?: boolean;
}


const WearableVisualization = ({
  showDayControls = false,
  showTapsData = false,
  dittiId,
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
          dittiId={dittiId}
          horizontalPadding={horizontalPadding} />
    </VisualizationController>
  );
};


export default WearableVisualization;
