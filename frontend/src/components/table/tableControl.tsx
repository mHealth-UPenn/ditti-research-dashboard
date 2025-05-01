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
