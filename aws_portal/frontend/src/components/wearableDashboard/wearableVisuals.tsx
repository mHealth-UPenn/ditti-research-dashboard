/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { useSearchParams } from "react-router-dom";
import DittiDataContext from "../../contexts/dittiDataContext";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";
import useDittiData from "../../hooks/useDittiData";
import WearableVisualsContent from "./wearableVisualsContent";


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