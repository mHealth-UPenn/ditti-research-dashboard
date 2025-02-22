/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
