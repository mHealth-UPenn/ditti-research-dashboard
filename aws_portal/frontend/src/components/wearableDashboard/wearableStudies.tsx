import CoordinatorStudySubjectProvider from "../../contexts/coordinatorStudySubjectContext";
import StudiesProvider from "../../contexts/studiesContext";
import { ViewProps } from "../../interfaces";
import WearableStudiesContent from "./wearableStudiesContent";


export default function WearableStudies({
  flashMessage,
  goBack,
  handleClick,
}: ViewProps) {
  return (
      <StudiesProvider app={3}>
        <CoordinatorStudySubjectProvider>
          <WearableStudiesContent
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick} />
        </CoordinatorStudySubjectProvider>
      </StudiesProvider>
    );
}
