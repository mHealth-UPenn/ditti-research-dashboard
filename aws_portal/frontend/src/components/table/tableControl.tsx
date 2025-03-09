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

import React, { useState } from "react";
import { TextField } from "../fields/textField";
import SearchIcon from '@mui/icons-material/Search';

interface TableControlProps {
  control: React.ReactElement;
  controlWidth: number;
  includeControl: boolean;
  includeSearch: boolean;
  onSearch: (text: string) => void;
}

export const TableControl: React.FC<TableControlProps> = ({
  control,
  controlWidth,
  includeControl,
  includeSearch,
  onSearch,
}) => {
  const [value, setValue] = useState("");

  const handleKeyUp = (v: string) => {
    setValue(v);
    onSearch(v);
  }

  return (
    <div className="flex items-center justify-between mb-4">
      {includeControl &&
        <div style={{ width: controlWidth + "%" }}>
          {control}
        </div>
      }
      <div>
        {includeSearch &&
          <TextField
            type="text"
            placeholder="Search..."
            label=""
            onKeyup={handleKeyUp}
            feedback=""
            value={value}>
              <div className="pl-2 text-light">
                <SearchIcon />
              </div>
          </TextField>
        }
      </div>
    </div>
  );
};
