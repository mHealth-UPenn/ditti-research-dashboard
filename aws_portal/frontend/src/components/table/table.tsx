import * as React from "react";
import { renderToString } from "react-dom/server";
import { Component } from "react";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TableRow from "./tableRow";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import "./table.css";

/**
 * name: the name to display in the column header
 * searchable: whether the column is searchable
 * sortable: whether the column is sortable
 * width: the column's display width
 */
export interface Column {
  name: string;
  searchable: boolean;
  sortable: boolean;
  width: number;
}

/**
 * ascending: unsorted, descending, or ascending
 * name: the header's name to display
 * sortable: whether the header's column is sortable
 * width: the column's display width
 */
export interface Header {
  ascending: -1 | 0 | 1;
  name: string;
  sortable: boolean;
  width: number;
}

/**
 * A table cell to be passed to the table
 * contents: the contents of the cell to render
 * sortValue: the value to sort the cell on
 */
export interface TableData {
  contents: React.ReactElement;
  sortValue: string;
}

/**
 * A table cell as it used for rendering purposes
 * contents: the contents of the cell to render
 * searchable: whether the cell is in a searchable column
 * searchValue: the value used for searching
 * sortable: whether the cell is in a searchable column
 * width: the column's display width
 */
interface Row {
  contents: React.ReactElement;
  searchable: boolean;
  searchValue: string;
  sortable: boolean;
  sortValue: string;
  width: number;
}

/**
 * columns: the table columns
 * control: a control element (e.g., a create button)
 * controlWidth: the control's display width
 * data: an array of rows that are arrays of table cells
 * includeControl: whether to show the control element
 * includeSearch: whether to show the search bar
 * paginationPer: the number of rows to show per page
 * sortDefault: the name of the default sort column
 */
interface TableProps {
  columns: Column[];
  control: React.ReactElement;
  controlWidth: number;
  data: TableData[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}

/**
 * rows: an array of rows that are arrays of table cells
 * rowsFiltered: rows to render if the user is using the search bar
 * rowsRendered: rows that are currently displayed
 * headers: the table's headers
 * page: the current page to display
 * totalPages: the total number of pages that can be displayed
 */
interface TableState {
  rows: Row[][];
  rowsFiltered: Row[][];
  rowsRendered: React.ReactElement;
  headers: Header[];
  page: number;
  totalPages: number;
}

class Table extends React.Component<TableProps, TableState> {
  constructor(props: TableProps) {
    super(props);

    const { columns, data, paginationPer, sortDefault } = props;

    // map the table cells that were passed as props
    const rows = data.map((row) =>
      row.map((cell, i) => {
        return {
          contents: cell.contents,
          searchable: columns[i].searchable,
          searchValue: renderToString(cell.contents)
            .replace(/<(.+?)>/, "")
            .toLowerCase(),  // remove all html tags for searchable data
          sortable: columns[i].sortable,
          sortValue: cell.sortValue,
          width: columns[i].width
        };
      })
    );

    // start with an empty table
    const rowsRendered = <React.Fragment />;

    // map the columns to a set of headers
    const headers = columns.map((c): Header => {
      return {
        ascending: c.name === sortDefault ? 1 : -1,  // default sort is descending
        name: c.name,
        sortable: c.sortable,
        width: c.width
      };
    });

    // start on page 1
    const page = 1;

    // get the total number of pages
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

    // render page 1 of the table's rows
    this.renderRows(1, this.state.rows);
  }

  /**
   * Filter the table from the search bar
   * @param text - the text in the search bar
   */
  onSearch = (text: string) => {
    const { paginationPer } = this.props;
    const { rows } = this.state;

    // always set the page to page 1 when searching
    const page = 1;

    // filter the table's rows
    const rowsFiltered = rows.filter((row) =>
      row.some(
        (cell) =>
          cell.searchable && cell.searchValue.includes(text.toLowerCase())
      )
    );

    // get the total number of pages using the number of filtered rows
    const totalPages = Math.ceil(rowsFiltered.length / paginationPer);

    this.setState({ page, rowsFiltered, totalPages });
    this.renderRows(page, rowsFiltered);
  };

  /**
   * Sort the table
   * @param name - the name of the column to sort the table on
   * @param ascending - whether the sort is ascending
   */
  onSort = (name: string, ascending: boolean) => {
    const { headers, page, rowsFiltered } = this.state;

    // set this header to ascending/descending and all others to unsorted
    for (const h of headers) {
      h.ascending = h.name === name ? (ascending ? 1 : 0) : -1;
    }

    // sort all rows using the cell corresponding to this header's index
    const i = headers.findIndex((h) => h.name === name);
    rowsFiltered.sort((a, b) => {
      if (a[i].sortValue < b[i].sortValue) return ascending ? 1 : -1;
      else if (a[i].sortValue > b[i].sortValue) return ascending ? -1 : 1;
      else return 0;
    });

    this.setState({ headers, rowsFiltered });
    this.renderRows(page, rowsFiltered);
  };

  /**
   * Show a new page
   * @param page - the page to show
   */
  paginate = (page: number) => {

    // render rows using the new page
    this.renderRows(page, this.state.rowsFiltered);
    this.setState({ page });
  };

  /**
   * Rander the table's rows
   * @param page - the page to render
   * @param data - the rows to render (necessary for rendering a filtered set
   *               of rows)
   */
  renderRows(page: number, data: Row[][]) {
    const { paginationPer } = this.props;

    const rowsRendered = (
      <React.Fragment>

        {/* if there is data to display in the table */}
        {data.length ? (

          // render each row
          data
            .slice((page - 1) * paginationPer, page * paginationPer)  // this page
            .map((row, i) => (
              <TableRow
                key={i}
                data={row.map((cell) => {
                  return { contents: cell.contents, width: cell.width };
                })}
              />
            ))
        ) : (
          <tr className="bg-light">

            {/* empty table message */}
            <td className="border-light-t border-light-r no-data">
              <i>No data to display</i>
            </td>
          </tr>
        )}
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

        {/* the table control */}
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

        {/* the table */}
        <table className="border-light-t border-light-b border-light-l">

          {/*  the table header */}
          <thead>
            <TableHeader headers={headers} onSort={this.onSort} />
          </thead>

          {/* the table body */}
          <tbody>{rowsRendered}</tbody>
        </table>

        {/* table pagination */}
        <div className="table-pagination">
          <div className="table-pagination-control">

            {/* last page button */}
            <div
              className={
                "pagination-button bg-light border-light-t border-light-l border-light-b" +
                (page > 1 ? " pagination-button-active" : "")
              }
              onClick={() => page > 1 && this.paginate(page - 1)}
            >
              <Left />
            </div>

            {/* next page button */}
            <div
              className={
                "pagination-button bg-light border-light" +
                (page < totalPages ? " pagination-button-active" : "")
              }
              onClick={() => page < totalPages && this.paginate(page + 1)}
            >
              <Right />
            </div>

            {/* current page */}
            <span>
              Page {page} of {totalPages || 1}
            </span>
          </div>

          {/* X items if 1 page or X of Y items if multiple pages */}
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
