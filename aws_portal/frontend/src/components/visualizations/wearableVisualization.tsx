import VisualizationController from "./visualizationController";
import WearableVisualizationContent from "./wearableVisualizationContent";


const WearableVisualization = () => {
  return (
    <VisualizationController
      margin={{ top: 8, right: 30, bottom: 8, left: 40 }}>
        <WearableVisualizationContent />
    </VisualizationController>
  );
};


export default WearableVisualization;
