import { DittiDataProvider } from "../../contexts/dittiDataContext";
import { useDittiData } from "../../hooks/useDittiData";
import { Card } from "../cards/card";
import { SmallLoader } from "../loader/loader";
import { CoordinatorStudySubjectProvider } from "../../contexts/coordinatorStudySubjectContext";
import { Outlet } from "react-router-dom";
import { StudiesProvider } from "../../contexts/studiesContext";
import { ViewContainer } from "../containers/viewContainer/viewContainer";

// React Router container for the Ditti App Dashboard for wrapping it in context providers
export function DittiAppDashboard() {
  const { dataLoading } = useDittiData();

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
        <DittiDataProvider>
          <Outlet />
        </DittiDataProvider>
      </CoordinatorStudySubjectProvider>
    </StudiesProvider>
  );
}
