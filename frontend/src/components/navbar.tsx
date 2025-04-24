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

import { Link } from "react-router-dom";
import { useNavbar } from "../hooks/useNavbar";

export const Navbar = () => {
  const { breadcrumbs } = useNavbar();

  return (
    <div
      className="z-10 flex h-16 flex-shrink-0 select-none items-center bg-white
        shadow"
    >
      <div className="flex h-12 items-center pl-12">
        {breadcrumbs.map((b, i) => {
          // If this is the last breadcrumb or if there is no link associated with it
          if (i === breadcrumbs.length - 1 || b.link === null) {
            // Don't make the breadcrumb clickable
            return (
              <div key={i} className="flex items-center">
                <span>{b.name}&nbsp;&nbsp;/&nbsp;&nbsp;</span>
              </div>
            );
          } else {
            return (
              <>
                <div
                  className="flex cursor-pointer items-center text-link
                    hover:text-link-hover"
                >
                  <Link to={b.link}>
                    <span>{b.name}</span>
                  </Link>
                </div>
                <div>
                  <span>&nbsp;&nbsp;/&nbsp;&nbsp;</span>
                </div>
              </>
            );
          }
        })}
      </div>
    </div>
  );
};
