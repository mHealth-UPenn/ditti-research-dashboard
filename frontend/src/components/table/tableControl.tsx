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

import { useState } from "react";
import { TextField } from "../fields/textField";
import SearchIcon from "@mui/icons-material/Search";
import { TableControlProps } from "./table.types";

export const TableControl = ({
  control,
  controlWidth,
  includeControl,
  includeSearch,
  onSearch,
}: TableControlProps) => {
  const [value, setValue] = useState("");

  const handleKeyUp = (v: string) => {
    setValue(v);
    onSearch(v);
  };

  return (
    <div className="mb-4 flex items-center justify-between">
      {includeControl && (
        <div style={{ width: `${String(controlWidth)}%` }}>{control}</div>
      )}
      <div>
        {includeSearch && (
          <TextField
            type="text"
            placeholder="Search..."
            label=""
            onKeyup={handleKeyUp}
            feedback=""
            value={value}
          >
            <div className="pl-2 text-light">
              <SearchIcon />
            </div>
          </TextField>
        )}
      </div>
    </div>
  );
};
