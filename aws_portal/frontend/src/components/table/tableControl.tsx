import * as React from "react";
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
  return (
    <div className="flex justify-between mb-4">
      {includeControl &&
        <div style={{ width: controlWidth + "%" }}>
          {control}
        </div>
      }
      {includeSearch &&
        <TextField
          type="text"
          placeholder="Search..."
          prefill=""
          label=""
          onKeyup={onSearch}
          feedback="">
            <div className="flex items-center bg-dark h-full px-4">
              <SearchIcon />
            </div>
        </TextField>
      }
    </div>
  );
};

export default TableControl;
