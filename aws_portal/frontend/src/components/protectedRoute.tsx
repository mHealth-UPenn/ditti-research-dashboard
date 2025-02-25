import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FullLoader } from "../components/loader";

interface ProtectedRouteProps {
  children: React.ReactElement;
  authMethod: 'cognito' | 'researcher';
}

/**
 * Component for protecting routes, redirecting unauthenticated users to the login page.
 * Displays a loading spinner while authentication status is being checked.
 * @param children - The component to render if the user is authenticated.
 * @param authMethod - The required authentication method ('cognito', or 'researcher')
 * @returns The child component if authenticated, or a redirect to the login page otherwise.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, authMethod }) => {
  const {
    isCognitoAuthenticated, 
    isResearcherAuthenticated,
    isCognitoLoading, 
    isResearcherLoading 
  } = useAuth();

  if (authMethod === 'cognito') {
    if (isCognitoLoading) return <FullLoader loading={true} msg="Loading..." />;
    if (!isCognitoAuthenticated) return <Navigate to="/login" replace />;
    return children;
  }

  if (authMethod === 'researcher') {
    if (isResearcherLoading) return <FullLoader loading={true} msg="Loading..." />;
    if (!isResearcherAuthenticated) return <Navigate to="/coordinator/login" replace />;
    return children;
  }

  return null;
};

export default ProtectedRoute;
