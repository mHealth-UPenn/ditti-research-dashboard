import * as React from "react";
import { Component } from "react";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TableRow from "./tableRow";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import "./table.css";

interface TableProps {
  columns: {
    name: string;
    searchable: boolean;
    sortable: boolean;
    width: number;
  }[];
  control: React.ReactElement;
  controlWidth: number;
  data: {
    contents: React.ReactElement;
    name: string;
    searchValue: string;
    sortValue: string;
    width: number;
  }[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}

interface TableState {
  page: number;
  renderedRows: React.ReactElement;
  searchText: string;
  sortBy: string;
  totalPages: number;
}

class Table extends React.Component<TableProps, TableState> {
  constructor(props: TableProps) {
    super(props);
    const { data, paginationPer } = props;
    const totalPages = Math.ceil(data.length / paginationPer);

    this.state = {
      page: 1,
      renderedRows: this.renderRows(1),
      searchText: "",
      sortBy: "",
      totalPages: totalPages
    };
  }

  onSearch = (text: string) => {
    console.log(text);
  };

  onSort = (name: string, ascending: boolean) => {
    console.log(name, ascending);
  };

  paginate = (page: number) => {
    const renderedRows = this.renderRows(page);
    this.setState({ renderedRows });
    this.setState({ page });
  };

  renderRows(page: number) {
    const { data, paginationPer } = this.props;

    return (
      <React.Fragment>
        {data
          .slice((page - 1) * paginationPer, page * paginationPer)
          .map((row) => (
            <TableRow data={row} />
          ))}
      </React.Fragment>
    );
  }

  render() {
    const {
      columns,
      control,
      controlWidth,
      data,
      includeControl,
      includeSearch,
      paginationPer,
      sortDefault
    } = this.props;

    const { page, renderedRows, totalPages } = this.state;

    return (
      <div className="table-container">
        {includeControl || includeSearch ? (
          <TableControl
            control={control}
            controlWidth={controlWidth}
            includeControl={includeControl}
            includeSearch={includeSearch}
            onSearch={this.onSearch}
          />
        ) : (
          ""
        )}
        <table className="border-light-t border-light-b border-light-l">
          <TableHeader
            columns={columns}
            onSort={this.onSort}
            sortDefault={sortDefault}
          />
          {renderedRows}
        </table>
        <div className="table-pagination">
          <div className="table-pagination-control">
            <div
              className={
                "pagination-button border-light-l border-light-b" +
                (page > 1 ? " pagination-button-active" : "")
              }
              onClick={() => page > 1 && this.paginate(page - 1)}
            >
              <Left />
            </div>
            <div
              className={
                "pagination-button border-light-l border-light-b border-light-r" +
                (page < totalPages ? " pagination-button-active" : "")
              }
              onClick={() => page < totalPages && this.paginate(page + 1)}
            >
              <Right />
            </div>
            <span>
              Page {page} of {totalPages}
            </span>
          </div>
          <span>
            {(page - 1) * paginationPer + 1} - {page * paginationPer} of{" "}
            {data.length} items
          </span>
        </div>
      </div>
    );
  }
}

export default Table;
