import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FullLoader } from "../components/loader";

interface ProtectedRouteProps {
  children: React.ReactElement;
  authMethod: 'iam' | 'cognito';
}

/**
 * Component for protecting routes, redirecting unauthenticated users to the login page.
 * Displays a loading spinner while authentication status is being checked.
 * @param children - The component to render if the user is authenticated.
 * @param authMethod - The required authentication method ('iam' or 'cognito')
 * @returns The child component if authenticated, or a redirect to the login page otherwise.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, authMethod }) => {
  const { isIamAuthenticated, isCognitoAuthenticated, isIamLoading, isCognitoLoading } = useAuth();

  if (authMethod === 'iam') {
    if (isIamLoading) return <FullLoader loading={true} msg="Loading..." />;
    if (!isIamAuthenticated) return <Navigate to="/coordinator/login" replace />;
    return children;
  }

  if (authMethod === 'cognito') {
    if (isCognitoLoading) return <FullLoader loading={true} msg="Loading..." />;
    if (!isCognitoAuthenticated) return <Navigate to="/login" replace />;
    return children;
  }

  return null;
};

export default ProtectedRoute;
