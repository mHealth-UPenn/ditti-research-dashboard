import * as React from "react";
import { Component } from "react";

interface TableHeaderProps {
  columns: {
    name: string;
    searchable: boolean;
    sortable: boolean;
    width: number;
  }[];
  onSort: (name: string, ascending: boolean) => void;
  sortDefault: string;
}

// interface TableHeaderState {}

class TableHeader extends React.Component<TableHeaderProps, any> {
  render() {
    const { columns, onSort, sortDefault } = this.props;

    return (
      <tr>
        {columns.map((c) => (
          <th className="border-light-r" style={{ width: c.width + "%" }}>
            h.name
          </th>
        ))}
      </tr>
    );
  }
}

export default TableHeader;
