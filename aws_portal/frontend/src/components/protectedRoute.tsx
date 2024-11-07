import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FullLoader } from "../components/loader";

interface ProtectedRouteProps {
  children: React.ReactElement;
}

/**
 * Component for protecting routes, redirecting unauthenticated users to the login page.
 * Displays a loading spinner while authentication status is being checked.
 * @param children - The component to render if the user is authenticated.
 * @returns The child component if authenticated, or a redirect to the login page otherwise.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    // Display a full-screen loader while authentication is loading
    return <FullLoader loading={true} msg="Loading..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
