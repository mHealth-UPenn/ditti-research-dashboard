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
import DittiAppDashboard from "./components/dittiApp/dittiAppDashboard";
import StudySummary from "./components/dittiApp/studySummary";
import Subjects from "./components/dittiApp/subjects";
import SubjectsEdit from "./components/dittiApp/subjectsEdit";
import SubjectVisualsV2 from "./components/dittiApp/subjectVisualsV2";
import WearableDashboard from "./components/wearableDashboard/wearableDashboard";
import WearableStudies from "./components/wearableDashboard/wearableStudies";
import WearableStudySummary from "./components/wearableDashboard/wearableStudySummary";
import WearableVisuals from "./components/wearableDashboard/wearableVisuals";
import StudiesView from "./components/dittiApp/studiesView";
import Apps from "./components/apps";
import AudioFiles from "./components/dittiApp/audioFiles";
import AudioFileUpload from "./components/dittiApp/audioFileUpload";

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
            path: "",
            element: <Apps />,
          },
          {
            path: "admin",
            element: <AdminDashboard />,
            children: [
              {
                path: "",
                element: <Accounts />,
              },
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
          },
          {
            path: "ditti",
            element: <DittiAppDashboard />,
            children: [
              {
                path: "",
                element: <StudiesView />,
              },
              {
                path: "audio",
                element: <AudioFiles />
              },
              {
                path: "audio/upload",
                element: <AudioFileUpload />
              },
              {
                path: "study",
                element: <StudySummary />,
              },
              {
                path: "participants",
                element: <Subjects />,
              },
              {
                path: "participants/enroll",
                element: <SubjectsEdit />,
              },
              {
                path: "participants/edit",
                element: <SubjectsEdit />,
              },
              {
                path: "participants/view",
                element: <SubjectVisualsV2 />,
              },
            ]
          },
          {
            path: "wearable",
            element: <WearableDashboard />,
            children: [
              {
                path: "",
                element: <WearableStudies />,
              },
              {
                path: "study",
                element: <WearableStudySummary />,
              },
              {
                path: "participants",
                element: <Subjects />,
              },
              {
                path: "participants/enroll",
                element: <SubjectsEdit />,
              },
              {
                path: "participants/edit",
                element: <SubjectsEdit />,
              },
              {
                path: "participants/view",
                element: <WearableVisuals />,
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
