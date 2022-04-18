import * as React from "react";
import { Component } from "react";

interface TableHeaderProps {
  columns: {
    name: string;
    searchable: boolean;
    sortable: boolean;
  }[];
  onSort: (name: string, ascending: boolean) => void;
  sortDefault: string;
}

// interface TableHeaderState {}

class TableHeader extends React.Component<TableHeaderProps, any> {
  render() {
    return <div>TableHeader</div>;
  }
}

export default TableHeader;
