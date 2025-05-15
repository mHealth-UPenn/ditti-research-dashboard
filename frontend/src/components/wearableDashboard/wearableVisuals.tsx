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

import { useSearchParams } from "react-router-dom";
import { DittiDataProvider } from "../../contexts/dittiDataContext";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";
import { WearableVisualsContent } from "./wearableVisualsContent";

export function WearableVisuals() {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;
  const dittiId = searchParams.get("dittiId") ?? "";

  return (
    // Wrap the visualization in wearable and ditti data providers
    <CoordinatorWearableDataProvider dittiId={dittiId} studyId={studyId}>
      <DittiDataProvider>
        <WearableVisualsContent dittiId={dittiId} />
      </DittiDataProvider>
    </CoordinatorWearableDataProvider>
  );
}
