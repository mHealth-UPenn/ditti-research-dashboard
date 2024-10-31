import React from "react";
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import ReplayIcon from '@mui/icons-material/Replay';

import { useVisualizationContext } from "../../contexts/visualizationContext";


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
      <button
        className="button button-lg button-secondary"
        onClick={panLeft}>
        <KeyboardArrowLeftIcon />
      </button>
      <button
        className="button button-lg button-secondary mr-2"
        onClick={panRight}>
        <KeyboardArrowRightIcon />
      </button>
      <button
        className="button button-lg button-secondary"
        onClick={zoomIn}
        disabled={minRangeReached}>
        <AddIcon />
      </button>
      <button
        className="button button-lg button-secondary mr-2"
        onClick={zoomOut}
        disabled={maxRangeReached}>
        <RemoveIcon />
      </button>
      <button
        className="button button-lg button-primary"
        onClick={resetZoom}>
        <ReplayIcon />
      </button>
    </div>
  );
}


export default TapVisualizationButtons;
