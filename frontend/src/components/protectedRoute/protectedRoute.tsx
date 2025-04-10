/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
    isResearcherLoading 
  } = useAuth();

  if (authMethod === "participant") {
    if (isParticipantLoading) return <FullLoader loading={true} msg="Loading..." />;
    if (!isParticipantAuthenticated) return <Navigate to="/login" replace />;
    return <>{children}</>;
  }

  if (authMethod === "researcher") {
    if (isResearcherLoading) return <FullLoader loading={true} msg="Loading..." />;
    if (!isResearcherAuthenticated) return <Navigate to="/coordinator/login" replace />;
    return <>{children}</>;
  }

  return <></>;
};
