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

import { WearableVisualizationContent } from "./wearableVisualizationContent";
import { VisualizationContextProvider } from "../../contexts/visualizationContext";
import { WearableVisualizationProps } from "./visualizations.types";

export const WearableVisualization = ({
  showDayControls = false,
  showTapsData = false,
  dittiId,
  horizontalPadding = false,
}: WearableVisualizationProps) => {
  return (
    <VisualizationContextProvider
      defaultMargin={{
        top: 8,
        right: horizontalPadding ? 30 : 2,
        bottom: 8,
        left: horizontalPadding ? 40 : 2,
      }}
    >
      <WearableVisualizationContent
        showDayControls={showDayControls}
        showTapsData={showTapsData}
        dittiId={dittiId}
        horizontalPadding={horizontalPadding}
      />
    </VisualizationContextProvider>
  );
};
