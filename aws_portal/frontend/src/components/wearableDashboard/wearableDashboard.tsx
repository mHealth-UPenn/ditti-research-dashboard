import { PropsWithChildren } from "react";
import CoordinatorStudySubjectProvider from "../../contexts/coordinatorStudySubjectContext";
import { Outlet } from "react-router-dom";
import StudiesProvider from "../../contexts/studiesContext";


function WearableDashboard() {
  return (
    <StudiesProvider app={3}>
      <CoordinatorStudySubjectProvider app={3}>
        <Outlet />
      </CoordinatorStudySubjectProvider>
    </StudiesProvider>
  );
}


export default WearableDashboard;
