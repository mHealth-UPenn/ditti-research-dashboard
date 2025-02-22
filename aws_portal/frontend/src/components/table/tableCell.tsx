/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { PropsWithChildren } from "react";

interface TableCellProps {
  width: number;
  paddingX?: number;
  paddingY?: number;
}


const TableCell = ({
  width,
  paddingX,
  paddingY,
  children,
}: PropsWithChildren<TableCellProps>) => {
  let padding = "";
  if (paddingX !== undefined) {
    padding += `px-[${paddingX}px]`;
  } else {
    padding += "px-1 lg:px-2";
  }
  if (paddingY !== undefined) {
    padding += ` py-[${paddingX}px]`;
  } else {
    padding += " py-2";
  }

  return (
    <td
      className="border-t border-r border-light h-[inherit] p-0"
      style={{ width: `${width}%` }}>
        <div className={`w-full h-full flex items-center ${padding}`}>
          <div className={`max-w-[500px] truncate ${paddingY !== undefined ? "h-full" : ""} ${paddingX !== undefined ? "w-full" : ""}`}>
            {children}
          </div>
        </div>
    </td>
  );
};


export default TableCell;
