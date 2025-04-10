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

import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Outlet, RouteObject } from "react-router-dom";
import { ParticipantLoginPage } from "./pages/participantLoginPage";
import { ResearcherLoginPage } from "./pages/researcherLoginPage";
import { Dashboard } from "./components/dashboard/dashboard";
import { ParticipantDashboard } from "./components/participantDashboard/participantDashboard";
import { ProtectedRoute } from "./components/protectedRoute/protectedRoute";
import { AuthProvider } from "./contexts/authContext";
import { useDocumentTitle } from "./hooks/useDocumentTitle";
import "./index.css";
import "./output.css";
import { FullLoader } from "./components/loader/loader";
import { PrivacyPolicy } from "./pages/privacyPolicy";
import { TermsOfUse } from "./pages/termsOfUse";
import { Accounts } from "./components/adminDashboard/accounts";
import { AccountsEdit } from "./components/adminDashboard/accountsEdit";
import { AboutSleepTemplates } from "./components/adminDashboard/aboutSleepTemplates";
import { AboutSleepTemplatesEdit } from "./components/adminDashboard/aboutSleepTemplatesEdit";
import { AccessGroups } from "./components/adminDashboard/accessGroups";
import { AccessGroupsEdit } from "./components/adminDashboard/accessGroupsEdit";
import { Roles } from "./components/adminDashboard/roles";
import { RolesEdit } from "./components/adminDashboard/rolesEdit";
import { Studies } from "./components/adminDashboard/studies";
import { StudiesEdit } from "./components/adminDashboard/studiesEdit";
import { AdminDashboard } from "./components/adminDashboard/adminDashboard";
import { DittiAppDashboard } from "./components/dittiApp/dittiAppDashboard";
import { StudySummary } from "./components/dittiApp/studySummary";
import { Subjects } from "./components/dittiApp/subjects";
import { SubjectsEdit } from "./components/dittiApp/subjectsEdit";
import { SubjectVisualsV2 } from "./components/dittiApp/subjectVisuals";
import { WearableDashboard } from "./components/wearableDashboard/wearableDashboard";
import { WearableStudies } from "./components/wearableDashboard/wearableStudies";
import { WearableStudySummary } from "./components/wearableDashboard/wearableStudySummary";
import { WearableVisuals } from "./components/wearableDashboard/wearableVisuals";
import { StudiesView } from "./components/dittiApp/studiesView";
import { Apps } from "./components/apps";
import { AudioFiles } from "./components/dittiApp/audioFiles";
import { AudioFileUpload } from "./components/dittiApp/audioFileUpload";
import { WearableSubjects } from "./components/wearableDashboard/wearableSubjects";
import { WearableSubjectsEdit } from "./components/wearableDashboard/wearableSubjectsEdit";
import { FlashMessageContextProvider } from "./contexts/flashMessagesContext";
import { DataRetrievalTasks } from "./components/adminDashboard/dataRetrievalTasks";

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
 * 
 * `handle.breadcrumbs` is used to display breadcrumbs in the Navbar component. `handle.breadcrumbs` is an array of
 * objects with `name` and `link` keys. The `name` key is the breadcrumb text and the `link` key is the breadcrumb link.
 * Either can contain a template string that is automatically replaced with the `studySlug`, `sidParam`, and
 * `dittiIdParam` values. `link` can also be null if the breadcrumb is not meant to be clickable.
 */
const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute authMethod="participant">
            <ParticipantDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: "coordinator",
        element: (
          <ProtectedRoute authMethod='researcher'>
            <FlashMessageContextProvider>
              <FullLoader loading={false} msg="" />
              <Dashboard />
            </FlashMessageContextProvider>
          </ProtectedRoute>
        ),
        children: [
          {
            path: "",
            element: <Apps />,
            handle: {
              breadcrumbs: [{ name: "Home", link: "/coordinator" }],
            },
          },
          {
            path: "admin",
            element: <AdminDashboard />,
            handle: {
              breadcrumbs: [
                { name: "Home", link: "/coordinator" },
                { name: "Admin Dashboard", link: null },
              ],
            },
            children: [
              {
                path: "",
                element: <Accounts />,
                handle: {
                  breadcrumbs: [{ name: "Accounts", link: "/coordinator/admin/accounts" }],
                },
              },
              {
                path: "about-sleep-templates",
                element: <AboutSleepTemplates />,
                handle: {
                  breadcrumbs: [{ name: "About Sleep Templates", link: "/coordinator/admin/about-sleep-templates" }],
                },
              },
              {
                path: "about-sleep-templates/create",
                element: <AboutSleepTemplatesEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "About Sleep Templates", link: "/coordinator/admin/about-sleep-templates" },
                    { name: "Create", link: "/coordinator/admin/about-sleep-templates/create" }
                  ],
                },
              },
              {
                path: "about-sleep-templates/edit",
                element: <AboutSleepTemplatesEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "About Sleep Templates", link: "/coordinator/admin/about-sleep-templates" },
                    { name: "Edit", link: "/coordinator/admin/about-sleep-templates/edit" }
                  ],
                },
              },
              {
                path: "access-groups",
                element: <AccessGroups />,
                handle: {
                  breadcrumbs: [{ name: "Access Groups", link: "/coordinator/admin/access-groups" }],
                },
              },
              {
                path: "access-groups/create",
                element: <AccessGroupsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Access Groups", link: "/coordinator/admin/access-groups" },
                    { name: "Create", link: "/coordinator/admin/access-groups/create" }
                  ],
                },
              },
              {
                path: "access-groups/edit",
                element: <AccessGroupsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Access Groups", link: "/coordinator/admin/access-groups" },
                    { name: "Edit", link: "/coordinator/admin/access-groups/edit" }
                  ],
                },
              },
              {
                path: "accounts",
                element: <Accounts />,
                handle: {
                  breadcrumbs: [{ name: "Accounts", link: "/coordinator/admin/accounts" }],
                },
              },
              {
                path: "accounts/create",
                element: <AccountsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Accounts", link: "/coordinator/admin/accounts" },
                    { name: "Create", link: "/coordinator/admin/accounts/create" }
                  ],
                },
              },
              {
                path: "accounts/edit",
                element: <AccountsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Accounts", link: "/coordinator/admin/accounts" },
                    { name: "Edit", link: "/coordinator/admin/accounts/edit" }
                  ],
                },
              },
              {
                path: "data-retrieval-tasks",
                element: <DataRetrievalTasks />,
                handle: {
                  breadcrumbs: [{ name: "Data Retrieval Tasks", link: "/coordinator/admin/data-retrieval-tasks" }],
                },
              },
              {
                path: "roles",
                element: <Roles />,
                handle: {
                  breadcrumbs: [{ name: "Roles", link: "/coordinator/admin/roles" }],
                },
              },
              {
                path: "roles/create",
                element: <RolesEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Roles", link: "/coordinator/admin/roles" },
                    { name: "Create", link: "/coordinator/admin/roles/create" }
                  ],
                },
              },
              {
                path: "roles/edit",
                element: <RolesEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Roles", link: "/coordinator/admin/roles" },
                    { name: "Edit", link: "/coordinator/admin/roles/edit" }
                  ],
                },
              },
              {
                path: "studies",
                element: <Studies />,
                handle: {
                  breadcrumbs: [{ name: "Studies", link: "/coordinator/admin/studies" }],
                },
              },
              {
                path: "studies/create",
                element: <StudiesEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Studies", link: "/coordinator/admin/studies" },
                    { name: "Create", link: "/coordinator/admin/studies/create" }
                  ],
                },
              },
              {
                path: "studies/edit",
                element: <StudiesEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "Studies", link: "/coordinator/admin/studies" },
                    { name: "Edit", link: "/coordinator/admin/studies/edit" }
                  ],
                },
              },
            ]
          },
          {
            path: "ditti",
            element: <DittiAppDashboard />,
            handle: {
              breadcrumbs: [
                { name: "Home", link: "/coordinator" },
                { name: "Ditti App Dashboard", link: "/coordinator/ditti" }
              ],
            },
            children: [
              {
                path: "",
                element: <StudiesView />,
              },
              {
                path: "audio",
                element: <AudioFiles />,
                handle: {
                  breadcrumbs: [{ name: "Audio Files", link: "/coordinator/ditti/audio" }],
                },
              },
              {
                path: "audio/upload",
                element: <AudioFileUpload />,
                handle: {
                  breadcrumbs: [
                    { name: "Audio Files", link: "/coordinator/ditti/audio" },
                    { name: "Upload", link: "/coordinator/ditti/audio/upload" }
                  ],
                },
              },
              {
                path: "study",
                element: <StudySummary />,
                handle: {
                  breadcrumbs: [{ name: "{study}", link: "/coordinator/ditti/study?sid={sid}" }],
                },
              },
              {
                path: "participants",
                element: <Subjects />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/ditti/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/ditti/participants?sid={sid}" }
                  ],
                },
              },
              {
                path: "participants/enroll",
                element: <SubjectsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/ditti/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/ditti/participants?sid={sid}" },
                    { name: "Enroll", link: "/coordinator/ditti/participants/enroll?sid={sid}" }
                  ],
                },
              },
              {
                path: "participants/edit",
                element: <SubjectsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/ditti/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/ditti/participants?sid={sid}" },
                    { name: "Edit", link: "/coordinator/ditti/participants/edit?dittiId={dittiId}&sid={sid}" }
                  ],
                },
              },
              {
                path: "participants/view",
                element: <SubjectVisualsV2 />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/ditti/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/ditti/participants?sid={sid}" },
                    { name: "View", link: "/coordinator/ditti/participants/view?&dittiId={dittiId}&sid={sid}" }
                  ],
                },
              },
            ]
          },
          {
            path: "wearable",
            element: <WearableDashboard />,
            handle: {
              breadcrumbs: [
                { name: "Home", link: "/coordinator" },
                { name: "Wearable Dashboard", link: "/coordinator/wearable" }
              ],
            },
            children: [
              {
                path: "",
                element: <WearableStudies />,
              },
              {
                path: "study",
                element: <WearableStudySummary />,
                handle: {
                  breadcrumbs: [{ name: "{study}", link: "/coordinator/wearable/study?sid={sid}" }],
                },
              },
              {
                path: "participants",
                element: <WearableSubjects />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/wearable/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/wearable/participants?sid={sid}" }],
                },
              },
              {
                path: "participants/enroll",
                element: <WearableSubjectsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/wearable/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/wearable/participants?sid={sid}" },
                    { name: "Enroll", link: "/coordinator/wearable/participants/enroll?sid={sid}" }
                  ],
                },
              },
              {
                path: "participants/edit",
                element: <SubjectsEdit />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/wearable/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/wearable/participants?sid={sid}" },
                    { name: "Edit", link: "/coordinator/wearable/participants/edit?dittiId={dittiId}&sid={sid}" }
                  ],
                },
              },
              {
                path: "participants/view",
                element: <WearableVisuals />,
                handle: {
                  breadcrumbs: [
                    { name: "{study}", link: "/coordinator/wearable/study?sid={sid}" },
                    { name: "Participants", link: "/coordinator/wearable/participants?sid={sid}" },
                    { name: "View", link: "/coordinator/wearable/participants/view?dittiId={dittiId}&sid={sid}" }
                  ],
                },
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
        element: <ResearcherLoginPage />,
      },
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
