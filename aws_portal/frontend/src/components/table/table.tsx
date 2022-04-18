import * as React from "react";
import { Component } from "react";

interface TableProps {
  columns: {
    name: string;
    searchable: boolean;
    sortable: boolean;
    width: number;
  }[];
  control: React.ReactElement[];
  controlWidth: number;
  data: {
    contents: React.ReactElement;
    name: string;
    searchValue: string;
    sortValue: string;
  }[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}

interface TableState {
  page: number;
  searchText: string;
  sortBy: string;
}

class Table extends React.Component<TableProps, TableState> {
  render() {
    return <div>Table</div>;
  }
}

export default Table;
