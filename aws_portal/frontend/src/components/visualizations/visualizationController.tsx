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
        <div className="w-full flex items-center">
          <div ref={parentRef} className="w-[400px] md:w-[600px] lg:w-[700px] xl:w-[800px] 2xl:w-[1100px]">
            {children}
          </div>
        </div>
    </VisualizationContext.Provider>
  );
};

export default VisualizationController;
