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
        <div className="w-full flex justify-center">
          <div ref={parentRef} className="w-[400px] sm:w-[500px] md:w-[600px] lg:w-[800px] xl:w-[1100px] 2xl:w-[1400px]">
            {children}
          </div>
        </div>
    </VisualizationContext.Provider>
  );
};

export default VisualizationController;
