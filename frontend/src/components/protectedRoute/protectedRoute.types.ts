/**
 * The authentication method for the protected route.
 */
export type AuthMethod = "participant" | "researcher";

/**
 * Props for the ProtectedRoute component.
 * @property authMethod - The authentication method for the protected route.
 */
export interface ProtectedRouteProps {
  authMethod: AuthMethod;
}
