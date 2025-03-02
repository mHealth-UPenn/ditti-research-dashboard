import { DittiDataContext } from "../../contexts/dittiDataContext";
import { useDittiData } from "../../hooks/useDittiData";
import { Card } from "../cards/card";
import { SmallLoader } from "../loader";
import { CoordinatorStudySubjectProvider } from "../../contexts/coordinatorStudySubjectContext";
import { Outlet } from "react-router-dom";
import { StudiesProvider } from "../../contexts/studiesContext";
import { ViewContainer } from "../containers/viewContainer";


// React Router container for the Ditti App Dashboard for wrapping it in context providers
export function DittiAppDashboard() {
  const {
    dataLoading,
    taps,
    audioTaps,
    audioFiles,
    refreshAudioFiles,
  } = useDittiData();

  if (dataLoading) {
    return (
      <ViewContainer>
        <Card width="md">
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <StudiesProvider app={2}>
      <CoordinatorStudySubjectProvider app={2}>
        <DittiDataContext.Provider value={{
          dataLoading,
          taps,
          audioTaps,
          audioFiles,
          refreshAudioFiles,
        }}>
          <Outlet />
        </DittiDataContext.Provider>
      </CoordinatorStudySubjectProvider>
    </StudiesProvider>
  );
}
