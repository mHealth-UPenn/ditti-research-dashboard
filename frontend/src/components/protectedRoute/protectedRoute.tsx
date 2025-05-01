import { PropsWithChildren } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { FullLoader } from "../loader/loader";
import { ProtectedRouteProps } from "./protectedRoute.types";

/**
 * Component for protecting routes, redirecting unauthenticated users to the login page.
 * Displays a loading spinner while authentication status is being checked.
 * @param children - The component to render if the user is authenticated.
 * @param authMethod - The required authentication method ('participant', or 'researcher')
 * @returns The child component if authenticated, or a redirect to the login page otherwise.
 */
export const ProtectedRoute = ({
  children,
  authMethod,
}: PropsWithChildren<ProtectedRouteProps>) => {
  const {
    isParticipantAuthenticated,
    isResearcherAuthenticated,
    isParticipantLoading,
    isResearcherLoading,
  } = useAuth();

  if (authMethod === "participant") {
    if (isParticipantLoading)
      return <FullLoader loading={true} msg="Loading..." />;
    if (!isParticipantAuthenticated) return <Navigate to="/login" replace />;
    return <>{children}</>;
  } else {
    if (isResearcherLoading)
      return <FullLoader loading={true} msg="Loading..." />;
    if (!isResearcherAuthenticated)
      return <Navigate to="/coordinator/login" replace />;
    return <>{children}</>;
  }
};
