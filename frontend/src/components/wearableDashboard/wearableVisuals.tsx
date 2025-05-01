import { useSearchParams } from "react-router-dom";
import { DittiDataProvider } from "../../contexts/dittiDataContext";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";
import { WearableVisualsContent } from "./wearableVisualsContent";

export function WearableVisuals() {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;
  const dittiId = searchParams.get("dittiId") ?? "";

  return (
    // Wrap the visualization in wearable and ditti data providers
    <CoordinatorWearableDataProvider dittiId={dittiId} studyId={studyId}>
      <DittiDataProvider>
        <WearableVisualsContent dittiId={dittiId} />
      </DittiDataProvider>
    </CoordinatorWearableDataProvider>
  );
}
