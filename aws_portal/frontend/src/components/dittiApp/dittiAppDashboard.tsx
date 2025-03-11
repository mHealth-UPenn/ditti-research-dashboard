/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
