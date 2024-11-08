import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export const useDocumentTitle = (defaultTitle: string) => {
  const location = useLocation();

  useEffect(() => {
    const isParticipantRoute = location.pathname.startsWith("/participant");
    document.title = isParticipantRoute ? "Participant Portal" : defaultTitle;
  }, [location, defaultTitle]);
};
