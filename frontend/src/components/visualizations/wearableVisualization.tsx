import { WearableVisualizationContent } from "./wearableVisualizationContent";
import { VisualizationContextProvider } from "../../contexts/visualizationContext";
import { WearableVisualizationProps } from "./visualizations.types";

export const WearableVisualization = ({
  showDayControls = false,
  showTapsData = false,
  dittiId,
  horizontalPadding = false,
}: WearableVisualizationProps) => {
  return (
    <VisualizationContextProvider
      defaultMargin={{
        top: 8,
        right: horizontalPadding ? 30 : 2,
        bottom: 8,
        left: horizontalPadding ? 40 : 2,
      }}
    >
      <WearableVisualizationContent
        showDayControls={showDayControls}
        showTapsData={showTapsData}
        dittiId={dittiId}
        horizontalPadding={horizontalPadding}
      />
    </VisualizationContextProvider>
  );
};
