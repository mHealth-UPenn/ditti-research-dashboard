import { useSearchParams } from "react-router-dom";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import DittiDataContext from "../../contexts/dittiDataContext";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";
import useDittiData from "../../hooks/useDittiData";
import { IStudySubject, Study, ViewProps } from "../../interfaces";
import WearableVisualsContent from "./wearableVisualsContent";
import { useStudiesContext } from "../../contexts/studiesContext";


export default function WearableVisuals() {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;
  const dittiId = searchParams.get("dittiId") || "";

  const {
    dataLoading,
    taps,
    audioTaps,
    audioFiles,
    refreshAudioFiles,
  } = useDittiData();

  return (
    // Wrap the visualization in wearable and ditti data providers
    <CoordinatorWearableDataProvider dittiId={dittiId} studyId={studyId}>
        <DittiDataContext.Provider value={{
            dataLoading,
            taps,
            audioTaps,
            audioFiles,
            refreshAudioFiles,
          }}>
            <WearableVisualsContent dittiId={dittiId} />
        </DittiDataContext.Provider>
    </CoordinatorWearableDataProvider>
  );
}