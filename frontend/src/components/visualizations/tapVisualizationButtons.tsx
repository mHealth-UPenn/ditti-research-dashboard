import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
import ReplayIcon from "@mui/icons-material/Replay";

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
          className="rounded-l"
          onClick={panLeft}
        >
          <KeyboardArrowLeftIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="mr-2 rounded-r border-l-0"
          onClick={panRight}
        >
          <KeyboardArrowRightIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="rounded-l"
          onClick={zoomIn}
          disabled={minRangeReached}
        >
          <AddIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="tertiary"
          className="mr-2 rounded-r border-l-0"
          onClick={zoomOut}
          disabled={maxRangeReached}
        >
          <RemoveIcon />
        </Button>
        <Button
          square={true}
          size="sm"
          variant="primary"
          onClick={resetZoom}
          rounded={true}
        >
          <ReplayIcon />
        </Button>
      </div>
      <div>
        <span className="text-sm italic">Click and drag to zoom</span>
      </div>
    </div>
  );
};
