import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export const useDocumentTitle = (defaultTitle: string) => {
  const location = useLocation();

  useEffect(() => {
    const isCoordinatorRoute = location.pathname.startsWith("/coordinator");
    document.title = isCoordinatorRoute ? "AWS Portal" : defaultTitle;
  }, [location, defaultTitle]);
};
