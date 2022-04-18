import * as React from "react";
import { Component } from "react";

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
    return <div>TableControl</div>;
  }
}

export default TableControl;
