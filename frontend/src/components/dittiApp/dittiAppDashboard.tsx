/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

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
