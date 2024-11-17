import React from "react";
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import ReplayIcon from '@mui/icons-material/Replay';

import { useVisualizationContext } from "../../contexts/visualizationContext";
import Button from "../buttons/button";


const TapVisualizationButtons: React.FC = () => {
  const {
    minRangeReached,
    maxRangeReached,
    panLeft,
    panRight,
    zoomIn,
    zoomOut,
    resetZoom,
  } = useVisualizationContext();

  return (
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
  );
}


export default TapVisualizationButtons;
