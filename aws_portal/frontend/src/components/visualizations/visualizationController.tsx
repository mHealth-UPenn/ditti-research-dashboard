import { PropsWithChildren } from 'react';
import useVisualizationController from '../../hooks/useVisualizationController';
import VisualizationContext from '../../contexts/visualizationContext';


const VisualizationController = ({
    children,
}: PropsWithChildren<any>) => {
  const {
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
  } = useVisualizationController();

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
