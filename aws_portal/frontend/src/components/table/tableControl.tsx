import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import { ReactComponent as Search } from "../../icons/search.svg";

interface TableControlProps {
  control: React.ReactElement;
  controlWidth: number;
  includeControl: boolean;
  includeSearch: boolean;
  onSearch: (text: string) => void;
}

// interface TableControlState {}

class TableControl extends React.Component<TableControlProps, any> {
  render() {
    const { control, controlWidth, includeControl, includeSearch, onSearch } =
      this.props;

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
              <div
                className="table-search-svg bg-dark"
                style={{ margin: "-0.75rem 1rem -0.75rem -0.25rem" }}
              >
                <Search />
              </div>
            </TextField>
          </div>
        ) : (
          ""
        )}
      </div>
    );
  }
}

export default TableControl;
