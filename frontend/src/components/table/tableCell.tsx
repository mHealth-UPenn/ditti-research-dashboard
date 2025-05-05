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
