import DittiDataContext from "../../contexts/dittiDataContext";
import useDittiData from "../../hooks/useDittiData";
import Card from "../cards/card";
import { SmallLoader } from "../loader";
import CoordinatorStudySubjectProvider from "../../contexts/coordinatorStudySubjectContext";
import { Outlet } from "react-router-dom";


function DittiAppDashboard() {
  const {
    dataLoading,
    studies,
    taps,
    audioTaps,
    audioFiles,
    refreshAudioFiles,
  } = useDittiData();

  if (dataLoading) {
    return (
      <Card width="md">
        <SmallLoader />
      </Card>
    );
  }

  return (
    <CoordinatorStudySubjectProvider app={2}>
      <DittiDataContext.Provider value={{
        dataLoading,
        studies,
        taps,
        audioTaps,
        audioFiles,
        refreshAudioFiles,
      }}>
        <Outlet />
      </DittiDataContext.Provider>
    </CoordinatorStudySubjectProvider>
  );
}


export default DittiAppDashboard;
