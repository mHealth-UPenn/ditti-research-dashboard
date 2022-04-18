import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";

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
        includeSearch ?
        <div className="table-search">
          <TextField
            id="table-search-input"
            svg={<React.Fragment />}
            type="text"
            placeholder="Search..."
            prefill=""
            label=""
            feedback=""
          />
        </div>
        includeControl ?
        <div className="table-control" style={{ width: controlWidth + "%" }}>
          {control}
        </div>
      </div>
    );
  }
}

export default TableControl;
