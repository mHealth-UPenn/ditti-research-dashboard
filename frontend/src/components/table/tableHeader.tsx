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
