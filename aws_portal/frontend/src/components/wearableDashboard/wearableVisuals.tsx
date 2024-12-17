import DittiDataContext from "../../contexts/dittiDataContext";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";
import useDittiData from "../../hooks/useDittiData";
import { IStudySubject, Study, ViewProps } from "../../interfaces";
import WearableVisualsContent from "./wearableVisualsContent";

interface IWearableVisualsProps extends ViewProps {
  subject: IStudySubject;
  studyDetails: Study;
}


export default function WearableVisuals({
  flashMessage,
  goBack,
  handleClick,
  subject,
  studyDetails,
}: IWearableVisualsProps) {
  const {
    dataLoading,
    studies,
    taps,
    audioTaps,
    audioFiles,
    users,
    refreshAudioFiles,
    getUserByDittiId,
  } = useDittiData();

  return (
    <CoordinatorWearableDataProvider
      dittiId={subject.dittiId}
      studyId={studyDetails.id}>
        <DittiDataContext.Provider value={{
            dataLoading,
            studies,
            taps,
            audioTaps,
            audioFiles,
            users,
            refreshAudioFiles,
            getUserByDittiId,
          }}>
            <WearableVisualsContent
              flashMessage={flashMessage}
              goBack={goBack}
              handleClick={handleClick}
              studyDetails={studyDetails}
              studySubject={subject} />
        </DittiDataContext.Provider>
    </CoordinatorWearableDataProvider>
  );
}