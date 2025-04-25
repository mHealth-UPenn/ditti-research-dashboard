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

import { PropsWithChildren } from "react";
import { TableCellProps } from "./table.types";

export const TableCell = ({
  width,
  paddingX,
  paddingY,
  children,
}: PropsWithChildren<TableCellProps>) => {
  let padding = "";
  if (paddingX !== undefined) {
    padding += `px-[${String(paddingX)}px]`;
  } else {
    padding += "px-1 lg:px-2";
  }
  if (paddingY !== undefined) {
    padding += ` py-[${String(paddingY)}px]`;
  } else {
    padding += " py-2";
  }

  return (
    <td
      className="h-[inherit] border-r border-t border-light p-0"
      style={{ width: `${String(width)}%` }}
    >
      <div className={`flex size-full items-center ${padding}`}>
        <div
          className={`max-w-[500px] truncate
            ${paddingY !== undefined ? "h-full" : ""}
            ${paddingX !== undefined ? "w-full" : ""}`}
        >
          {children}
        </div>
      </div>
    </td>
  );
};
