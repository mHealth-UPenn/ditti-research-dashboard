/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { LinkComponent } from "../links/linkComponent";
import { Link } from "react-router-dom";
import { AdminNavbarProps } from "./adminDashboard.types";

export const AdminNavbar = ({ activeView }: AdminNavbarProps) => {
  const views = [
    {
      active: false,
      name: "Accounts",
      link: "/coordinator/admin/accounts",
    },
    {
      active: false,
      name: "Studies",
      link: "/coordinator/admin/studies",
    },
    {
      active: false,
      name: "Roles",
      link: "/coordinator/admin/roles",
    },
    {
      active: false,
      name: "Access Groups",
      link: "/coordinator/admin/access-groups",
    },
    {
      active: false,
      name: "About Sleep Templates",
      link: "/coordinator/admin/about-sleep-templates",
    },
    {
      active: false,
      name: "Data Retrieval Tasks",
      link: "/coordinator/admin/data-retrieval-tasks",
    },
  ];

  // Set the current view as active
  views.forEach((v) => {
    if (v.name === activeView) {
      v.active = true;
    }
  });

  return (
    <div
      className="justify-left flex select-none items-center whitespace-nowrap
        bg-white px-6 lg:px-12"
    >
      {/* If the view is active, highlight it using bg-dark */}
      {views.map((v, i) =>
        v.active ? (
          <div
            key={i}
            className="bg-dark flex h-full items-center justify-center p-4
              text-center lg:px-8"
          >
            {v.name}
          </div>
        ) : (
          <div key={i} className="flex h-full">
            <Link to={v.link}>
              <LinkComponent
                className="flex size-full items-center justify-center px-3
                  text-center no-underline hover:bg-extra-light lg:px-4 xl:px-8"
              >
                {v.name}
              </LinkComponent>
            </Link>
          </div>
        )
      )}
    </div>
  );
};
