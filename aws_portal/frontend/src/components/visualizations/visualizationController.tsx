import { PropsWithChildren } from 'react';
import { useVisualizationController } from '../../hooks/useVisualizationController';
import { VisualizationContext } from '../../contexts/visualizationContext';

interface VisualizationControllerProps {
  defaultMargin?: { top: number, right: number, bottom: number, left: number };
}


export const VisualizationController = ({
  defaultMargin = { top: 50, right: 30, bottom: 25, left: 60 },
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
  } = useVisualizationController(defaultMargin);

  return (
    <VisualizationContext.Provider value={{
        zoomDomain,
        minRangeReached,
        maxRangeReached,
        parentRef,
        width,
        height,
        defaultMargin,
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
