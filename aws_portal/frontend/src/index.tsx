import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Outlet, RouteObject } from "react-router-dom";
import LoginPage from "./pages/loginPage";
import ParticipantLoginPage from "./pages/participantLoginPage";
import Dashboard from "./components/dashboard";
import ParticipantDashboard from "./components/participantDashboard";
import ProtectedRoute from "./components/protectedRoute";
import { AuthProvider } from "./AuthContext";
import { useDocumentTitle } from "./hooks/useDocumentTitle";
import "./index.css";
import "./output.css";
import { FullLoader } from "./components/loader";

/**
 * Root component wrapped with AuthProvider for authentication context.
 */
const Root: React.FC = () => {
  useDocumentTitle("Participant Portal");

  return (
    <AuthProvider>
      <Outlet />
    </AuthProvider>
  );
};

/**
 * Define application routes with nested routes for protected areas and login pages.
 */
const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute authMethod='cognito'>
            <ParticipantDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: "coordinator",
        element: (
          <ProtectedRoute authMethod='iam'>
            <>
              <FullLoader loading={false} msg="" />
              <Dashboard />
            </>
          </ProtectedRoute>
        ),
      },
      {
        path: "login",
        element: <ParticipantLoginPage />,
      },
      {
        path: "coordinator/login",
        element: <LoginPage />,
      },
      // Additional routes can be added here
    ],
  },
] as RouteObject[]);

/**
 * Select the root container element and render the application.
 * Log an error if the root container is not found.
 */
const container = document.getElementById("root");
if (container) {
  const root = createRoot(container);
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  );
} else {
  console.error("Root container not found");
}
