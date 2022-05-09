import * as React from "react";
import { renderToString } from "react-dom/server";
import { Component } from "react";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TableRow from "./tableRow";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import "./table.css";

export interface Column {
  name: string;
  searchable: boolean;
  sortable: boolean;
  width: number;
}

export interface Header {
  ascending: -1 | 0 | 1;
  name: string;
  sortable: boolean;
  width: number;
}

interface TableData {
  contents: React.ReactElement;
  searchable: boolean;
  searchValue: string;
  sortable: boolean;
  sortValue: string;
  width: number;
}

interface TableProps {
  columns: Column[];
  control: React.ReactElement;
  controlWidth: number;
  data: {
    contents: React.ReactElement;
    sortValue: string;
  }[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}

interface TableState {
  rows: TableData[][];
  rowsFiltered: TableData[][];
  rowsRendered: React.ReactElement;
  headers: Header[];
  page: number;
  totalPages: number;
}

class Table extends React.Component<TableProps, TableState> {
  constructor(props: TableProps) {
    super(props);

    const { columns, data, paginationPer, sortDefault } = props;
    const rows = data.map((row) =>
      row.map((cell, i) => {
        return {
          contents: cell.contents,
          searchable: columns[i].searchable,
          searchValue: renderToString(cell.contents)
            .replace(/<(.+?)>/, "")
            .toLowerCase(),
          sortable: columns[i].sortable,
          sortValue: cell.sortValue,
          width: columns[i].width
        };
      })
    );

    const rowsRendered = <React.Fragment />;
    const headers = columns.map((c): Header => {
      return {
        ascending: c.name === sortDefault ? 1 : -1,
        name: c.name,
        sortable: c.sortable,
        width: c.width
      };
    });

    const page = 1;
    const totalPages = Math.ceil(data.length / paginationPer);

    this.state = {
      rows,
      rowsFiltered: rows,
      rowsRendered,
      headers,
      page,
      totalPages
    };
  }

  componentDidMount() {
    this.renderRows(1, this.state.rows);
  }

  onSearch = (text: string) => {
    const { paginationPer } = this.props;
    const { rows } = this.state;

    const page = 1;
    const rowsFiltered = rows.filter((row) =>
      row.some(
        (cell) =>
          cell.searchable && cell.searchValue.includes(text.toLowerCase())
      )
    );

    const totalPages = Math.ceil(rowsFiltered.length / paginationPer);

    this.setState({ page, rowsFiltered, totalPages });
    this.renderRows(page, rowsFiltered);
  };

  onSort = (name: string, ascending: boolean) => {
    const { headers, page, rowsFiltered } = this.state;

    for (const h of headers) {
      h.ascending = h.name === name ? (ascending ? 1 : 0) : -1;
    }

    const i = headers.findIndex((h) => h.name === name);
    rowsFiltered.sort((a, b) => {
      if (a[i].sortValue < b[i].sortValue) return ascending ? 1 : -1;
      else if (a[i].sortValue > b[i].sortValue) return ascending ? -1 : 1;
      else return 0;
    });

    this.setState({ headers, rowsFiltered });
    this.renderRows(page, rowsFiltered);
  };

  paginate = (page: number) => {
    this.renderRows(page, this.state.rowsFiltered);
    this.setState({ page });
  };

  renderRows(page: number, data: TableData[][]) {
    const { paginationPer } = this.props;

    const rowsRendered = (
      <React.Fragment>
        {data
          .slice((page - 1) * paginationPer, page * paginationPer)
          .map((row) => (
            <TableRow
              data={row.map((cell) => {
                return { contents: cell.contents, width: cell.width };
              })}
            />
          ))}
      </React.Fragment>
    );

    this.setState({ rowsRendered });
  }

  render() {
    const {
      control,
      controlWidth,
      includeControl,
      includeSearch,
      paginationPer
    } = this.props;

    const { headers, page, rowsFiltered, rowsRendered, totalPages } =
      this.state;

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
          <TableHeader headers={headers} onSort={this.onSort} />
          {rowsRendered}
        </table>
        <div className="table-pagination">
          <div className="table-pagination-control">
            <div
              className={
                "pagination-button bg-light border-light-t border-light-l border-light-b" +
                (page > 1 ? " pagination-button-active" : "")
              }
              onClick={() => page > 1 && this.paginate(page - 1)}
            >
              <Left />
            </div>
            <div
              className={
                "pagination-button bg-light border-light" +
                (page < totalPages ? " pagination-button-active" : "")
              }
              onClick={() => page < totalPages && this.paginate(page + 1)}
            >
              <Right />
            </div>
            <span>
              Page {page} of {totalPages || 1}
            </span>
          </div>
          <span>
            {totalPages
              ? `${(page - 1) * paginationPer + 1} - ${Math.min(
                  rowsFiltered.length,
                  page * paginationPer
                )} of `
              : ""}
            {rowsFiltered.length} item{rowsFiltered.length === 1 ? "" : "s"}
          </span>
        </div>
      </div>
    );
  }
}

export default Table;
