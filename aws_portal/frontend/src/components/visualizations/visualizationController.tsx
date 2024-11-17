import { PropsWithChildren } from 'react';
import useVisualizationController from '../../hooks/useVisualizationController';
import VisualizationContext from '../../contexts/visualizationContext';

interface VisualizationControllerProps {
  margin?: { top: number, right: number, bottom: number, left: number };
}


const VisualizationController = ({
  margin = { top: 50, right: 30, bottom: 25, left: 60 },
  children,
}: PropsWithChildren<VisualizationControllerProps>) => {
  const {
    zoomDomain,
    minRangeReached,
    maxRangeReached,
    parentRef,
    width,
    height,
    xScale,
    xTicks,
    onZoomChange,
    resetZoom,
    panLeft,
    panRight,
    zoomIn,
    zoomOut,
  } = useVisualizationController(margin);

  return (
    <VisualizationContext.Provider value={{
        zoomDomain,
        minRangeReached,
        maxRangeReached,
        parentRef,
        width,
        height,
        margin,
        xScale,
        xTicks,
        onZoomChange,
        resetZoom,
        panLeft,
        panRight,
        zoomIn,
        zoomOut,
      }}>
        <div ref={parentRef} className="w-full">
          {children}
        </div>
    </VisualizationContext.Provider>
  );
};

export default VisualizationController;
