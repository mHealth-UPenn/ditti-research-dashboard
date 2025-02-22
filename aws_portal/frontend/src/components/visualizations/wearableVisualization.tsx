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

import VisualizationController from "./visualizationController";
import WearableVisualizationContent from "./wearableVisualizationContent";

/**
 * Props to pass to the wearable visualization.
@ @property showDayControls: `showDayControls` to pass to `WearableVisualizationContent`.
@ @property showTapsData: `showTapsData` to pass to `WearableVisualizationContent`.
@ @property dittiId: `dittiId` to pass to `WearableVisualizationContent`.
@ @property horizontalPadding: Whether to add horizontal padding to the visualization.
 */
interface IWearableVisualizationProps {
  showDayControls?: boolean;
  showTapsData?: boolean;
  dittiId?: string;
  horizontalPadding?: boolean;
}


const WearableVisualization = ({
  showDayControls = false,
  showTapsData = false,
  dittiId,
  horizontalPadding = false,
}: IWearableVisualizationProps) => {
  return (
    <VisualizationController
      defaultMargin={{
        top: 8,
        right: horizontalPadding ? 30 : 2,
        bottom: 8,
        left: horizontalPadding ? 40 : 2
      }}>
        <WearableVisualizationContent
          showDayControls={showDayControls}
          showTapsData={showTapsData}
          dittiId={dittiId}
          horizontalPadding={horizontalPadding} />
    </VisualizationController>
  );
};


export default WearableVisualization;
