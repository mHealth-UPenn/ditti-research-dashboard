import React, { useState, useEffect, useCallback } from "react";
import { renderToString } from "react-dom/server";
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

const Table: React.FC<TableProps> = ({
  columns,
  control,
  controlWidth,
  data,
  includeControl,
  includeSearch,
  paginationPer,
  sortDefault
}) => {
  const [rows, setRows] = useState<Row[][]>(() =>
    data.map((row) =>
      row.map((cell, i) => ({
        contents: cell.contents,
        searchable: columns[i].searchable,
        searchValue: renderToString(cell.contents)
          .replace(/<(.+?)>/g, "")
          .toLowerCase(),
        sortable: columns[i].sortable,
        sortValue: cell.sortValue,
        width: columns[i].width
      }))
    )
  );

  const [rowsFiltered, setRowsFiltered] = useState<Row[][]>(rows);
  const [rowsRendered, setRowsRendered] = useState<React.ReactElement>(
    <React.Fragment />
  );
  const [headers, setHeaders] = useState<Header[]>(
    columns.map((c) => ({
      ascending: c.name === sortDefault ? 1 : -1,
      name: c.name,
      sortable: c.sortable,
      width: c.width
    }))
  );
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(
    Math.ceil(data.length / paginationPer)
  );

  useEffect(() => {
    renderRows(1, rows);
  }, [rows]);

  const onSearch = useCallback(
    (text: string) => {
      const filtered = rows.filter((row) =>
        row.some(
          (cell) =>
            cell.searchable && cell.searchValue.includes(text.toLowerCase())
        )
      );

      setRowsFiltered(filtered);
      setPage(1);
      setTotalPages(Math.ceil(filtered.length / paginationPer));
      renderRows(1, filtered);
    },
    [rows, paginationPer]
  );

  const onSort = useCallback(
    (name: string, ascending: boolean) => {
      const updatedHeaders: Header[] = headers.map((header) => ({
        ...header,
        ascending: header.name === name ? (ascending ? 1 : 0) : -1
      }));

      const sortedRows = [...rowsFiltered].sort((a, b) => {
        const index = updatedHeaders.findIndex((h) => h.name === name);
        if (a[index].sortValue < b[index].sortValue) return ascending ? 1 : -1;
        else if (a[index].sortValue > b[index].sortValue) return ascending ? -1 : 1;
        else return 0;
      });

      setHeaders(updatedHeaders);
      setRowsFiltered(sortedRows);
      renderRows(page, sortedRows);
    },
    [headers, page, rowsFiltered]
  );

  const paginate = useCallback(
    (newPage: number) => {
      renderRows(newPage, rowsFiltered);
      setPage(newPage);
    },
    [rowsFiltered]
  );

  const renderRows = useCallback(
    (currentPage: number, dataToRender: Row[][]) => {
      const fragment = (
        <React.Fragment>
          {dataToRender.length ? (
            dataToRender
              .slice((currentPage - 1) * paginationPer, currentPage * paginationPer)
              .map((row, i) => (
                <TableRow
                  key={i}
                  data={row.map((cell) => ({
                    contents: cell.contents,
                    width: cell.width
                  }))}
                />
              ))
          ) : (
            <tr className="bg-light">
              <td className="border-light-t border-light-r no-data">
                <i>No data to display</i>
              </td>
            </tr>
          )}
        </React.Fragment>
      );
      setRowsRendered(fragment);
    },
    [paginationPer]
  );

  return (
    <div className="table-container">
      {includeControl || includeSearch ? (
        <TableControl
          control={control}
          controlWidth={controlWidth}
          includeControl={includeControl}
          includeSearch={includeSearch}
          onSearch={onSearch}
        />
      ) : null}

      <table className="border-light-t border-light-b border-light-l">
        <thead>
          <TableHeader headers={headers} onSort={onSort} />
        </thead>
        <tbody>{rowsRendered}</tbody>
      </table>

      <div className="table-pagination">
        <div className="table-pagination-control">
          <div
            className={
              "pagination-button bg-light border-light-t border-light-l border-light-b" +
              (page > 1 ? " pagination-button-active" : "")
            }
            onClick={() => page > 1 && paginate(page - 1)}
          >
            <Left />
          </div>
          <div
            className={
              "pagination-button bg-light border-light" +
              (page < totalPages ? " pagination-button-active" : "")
            }
            onClick={() => page < totalPages && paginate(page + 1)}
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
};

export default Table;
