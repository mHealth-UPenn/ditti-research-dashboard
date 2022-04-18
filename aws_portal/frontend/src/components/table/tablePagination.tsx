import * as React from "react";
import { Component } from "react";

interface TablePaginationProps {
  onClick: (page: number) => void;
  paginationPer: number;
  totalRows: number;
}

interface TablePaginationState {
  page: number;
}

class TablePagination extends React.Component<
  TablePaginationProps,
  TablePaginationState
> {
  render() {
    return <div className="table-pagination">TablePagination</div>;
  }
}

export default TablePagination;
