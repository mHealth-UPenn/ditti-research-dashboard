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
          <td
            className="border-light-t border-light-r"
            style={{ width: cell.width + "%" }}
          >
            {cell.contents}
          </td>
        ))}
      </tr>
    );
  }
}

export default TableRow;
