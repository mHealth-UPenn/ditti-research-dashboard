import * as React from "react";
import { Component } from "react";

interface TableRowProps {
  data: {
    contents: React.ReactElement;
    name: string;
    searchValue: string;
    sortValue: string;
    width: number;
  }[];
}

// interface TableRowState {}

class TableRow extends React.Component<TableRowProps, any> {
  render() {
    const { data } = this.props;

    return (
      <tr>
        {data.map((cell) => (
          <th style={{ width: cell.width + "%" }}>{cell.contents}</th>
        ))}
      </tr>
    );
  }
}

export default TableRow;
