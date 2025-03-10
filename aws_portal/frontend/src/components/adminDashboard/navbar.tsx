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

import LinkComponent from "../links/linkComponent";
import { Link } from "react-router-dom";


/**
 * @property {string} activeView - The name of the active view
 */
interface NavbarProps {
  activeView: "Accounts" | "Studies" | "Roles" | "Access Groups" | "About Sleep Templates" | "Data Retrieval Tasks";
}

const Navbar = ({ activeView }: NavbarProps) => {
  const views = [
    {
      active: false,
      name: "Accounts",
      link: "/coordinator/admin/accounts"
    },
    {
      active: false,
      name: "Studies",
      link: "/coordinator/admin/studies"
    },
    {
      active: false,
      name: "Roles",
      link: "/coordinator/admin/roles"
    },
    {
      active: false,
      name: "Access Groups",
      link: "/coordinator/admin/access-groups"
    },
    {
      active: false,
      name: "About Sleep Templates",
      link: "/coordinator/admin/about-sleep-templates"
    },
    {
      active: false,
      name: "Data Retrieval Tasks",
      link: "/coordinator/admin/data-retrieval-tasks"
    }
  ];

  // Set the current view as active
  views.forEach(v => {
    if (v.name === activeView) {
      v.active = true;
    }
  });

  return (
    <div className="flex items-center justify-left px-6 lg:px-12 bg-white select-none whitespace-nowrap">
      {/* If the view is active, highlight it using bg-dark */}
      {views.map((v, i) => (
        v.active ?
          <div
            key={i}
            className="flex px-4 lg:px-8 items-center justify-center h-full py-4 bg-dark text-center">
              {v.name}
          </div> :
          <div key={i} className="flex h-full">
            <Link to={v.link}>
              <LinkComponent className="flex items-center justify-center px-3 lg:px-4 xl:px-8 h-full w-full no-underline hover:bg-extra-light text-center">
                  {v.name}
              </LinkComponent>
            </Link>
          </div>
      ))}
    </div>
  );
};

export default Navbar;
