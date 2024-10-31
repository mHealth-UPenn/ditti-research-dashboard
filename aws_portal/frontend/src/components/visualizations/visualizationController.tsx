import React, { PropsWithChildren } from 'react';
import useVisualizationController from '../../hooks/useVisualizationController';
import VisualizationContext from '../../contexts/visualizationContext';


const VisualizationController = ({
    children,
}: PropsWithChildren<any>) => {
  const {
    zoomDomain,
    minRangeReached,
    maxRangeReached,
    width,
    height,
    margin,
    xScale,
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
        width,
        height,
        margin,
        xScale,
        onZoomChange,
        resetZoom,
        panLeft,
        panRight,
        zoomIn,
        zoomOut,
      }}>
        {children}
    </VisualizationContext.Provider>
  );
};

export default VisualizationController;
