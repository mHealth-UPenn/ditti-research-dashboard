import * as React from "react";
import { Component } from "react";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";

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
    return (
      <div className="table-pagination">
        <div className="table-pagination-control">
          <div className="pagination-button border-light-l border-light-b">
            <Left />
          </div>
          <div className="pagination-button border-light-l border-light-b border-light-r">
            <Right />
          </div>
          <span>Page 1 of 1</span>
        </div>
        <span>1 - 10 of 20 items</span>
      </div>
    );
  }
}

export default TablePagination;
