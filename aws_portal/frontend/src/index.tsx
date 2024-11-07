import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Outlet, RouteObject } from "react-router-dom";
import LoginPage from "./loginPage";
import Dashboard from "./components/dashboard";
import ProtectedRoute from "./components/protectedRoute";
import { AuthProvider } from "./AuthContext";
import "./index.css";
import "./output.css";

/**
 * Root component wrapped with AuthProvider for authentication context.
 */
const Root: React.FC = () => (
  <AuthProvider>
    <Outlet />
  </AuthProvider>
);

/**
 * Define application routes with nested routes for protected areas and login page.
 */
const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        path: "login",
        element: <LoginPage />,
      },
      {
        path: "/",
        element: (
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        ),
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
