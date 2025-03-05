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
import { IBreadcrumb } from "../interfaces";
import { useNavbarContext } from "../contexts/navbarContext";

interface IHandle {
  breadcrumbs: IBreadcrumb[];
}


const Navbar = () => {
  const { breadcrumbs } = useNavbarContext();

  return (
    <div className="bg-white flex items-center h-16 flex-shrink-0 select-none z-10 shadow">
      <div className="flex items-center h-12 pl-12">
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
                <div className="flex items-center text-link hover:text-link-hover cursor-pointer">
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
}

export default Navbar;
