import * as React from "react";
import { Component } from "react";

interface TableRowProps {
  data: {
    contents: React.ReactElement;
    name: string;
    searchValue: string;
    sortValue: string;
  }[];
}

// interface TableRowState {}

class TableRow extends React.Component<TableRowProps, any> {
  render() {
    return <div>TableRow</div>;
  }
}

export default TableRow;
