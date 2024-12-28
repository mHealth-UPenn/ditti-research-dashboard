import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Outlet, RouteObject } from "react-router-dom";
import LoginPage from "./pages/loginPage";
import ParticipantLoginPage from "./pages/participantLoginPage";
import Dashboard from "./components/dashboard";
import ParticipantDashboard from "./components/participantDashboard/participantDashboard";
import ProtectedRoute from "./components/protectedRoute";
import { AuthProvider } from "./AuthContext";
import { useDocumentTitle } from "./hooks/useDocumentTitle";
import "./index.css";
import "./output.css";
import { FullLoader } from "./components/loader";
import PrivacyPolicy from "./pages/privacyPolicy";
import TermsOfUse from "./pages/termsOfUse";
import Accounts from "./components/adminDashboard/accounts";
import AccountsEdit from "./components/adminDashboard/accountsEdit";
import AboutSleepTemplates from "./components/adminDashboard/aboutSleepTemplates";
import AboutSleepTemplatesEdit from "./components/adminDashboard/aboutSleepTemplatesEdit";
import AccessGroups from "./components/adminDashboard/accessGroups";
import AccessGroupsEdit from "./components/adminDashboard/accessGroupsEdit";
import Roles from "./components/adminDashboard/roles";
import RolesEdit from "./components/adminDashboard/rolesEdit";
import Studies from "./components/adminDashboard/studies";
import StudiesEdit from "./components/adminDashboard/studiesEdit";
import AdminDashboard from "./components/adminDashboard/adminDashboard";

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
        children: [
          {
            path: "admin",
            element: <AdminDashboard />,
            children: [
              {
                path: "about-sleep-templates",
                element: <AboutSleepTemplates />,
              },
              {
                path: "about-sleep-templates/create",
                element: <AboutSleepTemplatesEdit />
              },
              {
                path: "about-sleep-templates/edit",
                element: <AboutSleepTemplatesEdit />
              },
              {
                path: "access-groups",
                element: <AccessGroups />,
              },
              {
                path: "access-groups/create",
                element: <AccessGroupsEdit />
              },
              {
                path: "access-groups/edit",
                element: <AccessGroupsEdit />
              },
              {
                path: "accounts",
                element: <Accounts />,
              },
              {
                path: "accounts/create",
                element: <AccountsEdit />
              },
              {
                path: "accounts/edit",
                element: <AccountsEdit />
              },
              {
                path: "roles",
                element: <Roles />,
              },
              {
                path: "roles/create",
                element: <RolesEdit />
              },
              {
                path: "roles/edit",
                element: <RolesEdit />
              },
              {
                path: "studies",
                element: <Studies />,
              },
              {
                path: "studies/create",
                element: <StudiesEdit />
              },
              {
                path: "studies/edit",
                element: <StudiesEdit />
              },
            ]
          }
        ]
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
  {
    path: "/privacy-policy",
    element: <PrivacyPolicy />,
  },
  {
    path: "/terms-of-use",
    element: <TermsOfUse />,
  }
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
