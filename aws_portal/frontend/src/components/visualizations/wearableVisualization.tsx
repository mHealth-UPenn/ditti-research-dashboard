import { VisualizationController } from "./visualizationController";
import { WearableVisualizationContent } from "./wearableVisualizationContent";

/**
 * Props to pass to the wearable visualization.
@ @property showDayControls: `showDayControls` to pass to `WearableVisualizationContent`.
@ @property showTapsData: `showTapsData` to pass to `WearableVisualizationContent`.
@ @property dittiId: `dittiId` to pass to `WearableVisualizationContent`.
@ @property horizontalPadding: Whether to add horizontal padding to the visualization.
 */
interface IWearableVisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  dittiId?: string;
  horizontalPadding?: boolean;
}


export const WearableVisualization = ({
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
