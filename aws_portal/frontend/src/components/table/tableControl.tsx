import * as React from "react";
import TextField from "../fields/textField";
import { ReactComponent as Search } from "../../icons/search.svg";

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
    <div className="table-control-container">
      {includeControl ? (
        <div className="table-control" style={{ width: controlWidth + "%" }}>
          {control}
        </div>
      ) : (
        ""
      )}
      {includeSearch ? (
        <div className="table-search">
          <TextField
            id="table-search-input"
            type="text"
            placeholder="Search..."
            prefill=""
            label=""
            onKeyup={onSearch}
            feedback=""
          >
            <div className="table-search-svg bg-dark">
              <Search />
            </div>
          </TextField>
        </div>
      ) : (
        ""
      )}
    </div>
  );
};

export default TableControl;
