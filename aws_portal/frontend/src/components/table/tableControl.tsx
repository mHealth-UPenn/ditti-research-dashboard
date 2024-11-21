import React, { useState } from "react";
import TextField from "../fields/textField";
import SearchIcon from '@mui/icons-material/Search';

interface TableControlProps {
  control: React.ReactElement;
  controlWidth: number;
  includeControl: boolean;
  includeSearch: boolean;
  onSearch: (text: string) => void;
}

const TableControl: React.FC<TableControlProps> = ({
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

export default TableControl;
