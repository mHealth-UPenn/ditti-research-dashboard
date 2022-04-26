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
      <div className="table-control-container border-light-t border-light-r border-light-l">
        {includeSearch ? (
          <div className="table-search">
            <div className="table-search-svg bg-dark">
              <Search />
            </div>
            <TextField
              id="table-search-input"
              svg={<React.Fragment />}
              type="text"
              placeholder="Search..."
              prefill=""
              label=""
              onKeyup={onSearch}
              feedback=""
            />
          </div>
        ) : (
          ""
        )}
        {includeControl ? (
          <div className="table-control" style={{ width: controlWidth + "%" }}>
            {control}
          </div>
        ) : (
          ""
        )}
      </div>
    );
  }
}

export default TableControl;
