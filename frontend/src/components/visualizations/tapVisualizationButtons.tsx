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

import React from "react";
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import ReplayIcon from '@mui/icons-material/Replay';

import { useVisualization } from "../../hooks/useVisualization";
import { Button } from "../buttons/button";


export const TapVisualizationButtons = () => {
  const {
    minRangeReached,
    maxRangeReached,
    panLeft,
    panRight,
    zoomIn,
    zoomOut,
    resetZoom,
  } = useVisualization();

  return (
    <div className="flex flex-col items-end">
      <div className="flex justify-end">
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="rounded-l-[0.25rem]"
          onClick={panLeft}>
          <KeyboardArrowLeftIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="mr-2 border-l-0 rounded-r-[0.25rem]"
          onClick={panRight}>
          <KeyboardArrowRightIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="rounded-l-[0.25rem]"
          onClick={zoomIn}
          disabled={minRangeReached}>
          <AddIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="mr-2 border-l-0 rounded-r-[0.25rem]"
          onClick={zoomOut}
          disabled={maxRangeReached}>
          <RemoveIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="primary"
          onClick={resetZoom}
          rounded={true}>
          <ReplayIcon />
        </Button>
      </div>
      <div>
        <span className="italic text-sm">Click and drag to zoom</span>
      </div>
    </div>
  );
}
