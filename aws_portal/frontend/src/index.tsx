import React from "react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import LoginPage from "./loginPage";
import Dashboard from "./components/dashboard";
import "./index.css";
import "./output.css";

const isAuthenticated = (): boolean => {
  // TODO: Add full authentication logic
  return !!localStorage.getItem("jwt");
};

const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const router = createBrowserRouter([
  {
    path: "/login",
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
]);

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
