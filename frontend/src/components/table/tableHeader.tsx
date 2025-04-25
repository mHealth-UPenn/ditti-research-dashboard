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

import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { TableHeaderProps } from "./table.types";

export const TableHeader = ({ headers, onSort }: TableHeaderProps) => {
  return (
    <tr className="h-12">
      {headers.map((h, i) => (
        <th
          key={i}
          className={`select-none border-r border-light bg-extra-light
          ${h.sortable ? "cursor-pointer" : ""}`}
          style={{ width: `${String(h.width)}%` }}
          onClick={() => {
            if (h.sortable) {
              onSort(h.name, h.ascending ? 0 : 1);
            }
          }}
        >
          <div
            className="items-begin relative mx-1 flex justify-between lg:mx-2"
          >
            <span className="font-regular whitespace-nowrap text-base">
              {h.name}
            </span>

            {/* sort buttons */}
            {h.sortable &&
              (h.ascending === -1 ? (
                <KeyboardArrowUpIcon className="text-light" />
              ) : h.ascending === 0 ? (
                <KeyboardArrowDownIcon />
              ) : (
                <KeyboardArrowUpIcon />
              ))}
          </div>
        </th>
      ))}
    </tr>
  );
};
