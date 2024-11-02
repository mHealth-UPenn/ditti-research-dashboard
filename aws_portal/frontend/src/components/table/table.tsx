import React, { useState, useEffect, useCallback, useMemo } from "react";
import { renderToString } from "react-dom/server";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TableRow from "./tableRow";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';


import "./table.css";
import Button from "../buttons/button";

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
  sortValue?: string;
  searchValue?: string;
  paddingX?: number;
  paddingY?: number;
}

/**
 * A table cell as it used for rendering purposes
 * contents: the contents of the cell to render
 * searchable: whether the cell is in a searchable column
 * searchValue: the value used for searching
 * sortable: whether the cell is in a searchable column
 * width: the column's display width
 */
interface Cell {
  contents: React.ReactElement;
  searchable: boolean;
  searchValue: string;
  sortable: boolean;
  sortValue: string;
  width: number;
  paddingX?: number;
  paddingY?: number;
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
  const cells: Cell[][] = useMemo(() =>
    data.map((row) =>
      row.map((cell, i) => ({
        contents: cell.contents,
        searchable: columns[i].searchable,
        searchValue: (
          cell.searchValue ?
          renderToString(cell.contents)
            .replace(/<(.+?)>/g, "")
            .toLowerCase() :
          ""
        ),
        sortable: columns[i].sortable,
        sortValue: cell.sortValue || "",
        width: columns[i].width,
        paddingX: cell.paddingX,
        paddingY: cell.paddingY,
      }))
    ), [data]
  );

  const [rowsFiltered, setRowsFiltered] = useState<Cell[][]>(cells);
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

  useEffect(() => renderRows(1, cells), [cells]);

  const onSearch = useCallback(
    (text: string) => {
      const filtered = cells.filter((row) =>
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
    [cells, paginationPer]
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

  const renderRows = (currentPage: number, dataToRender: Cell[][]) => {
    const fragment = (
      <>
        {dataToRender.length ?
          dataToRender
            .slice((currentPage - 1) * paginationPer, currentPage * paginationPer)
            .map((row, i) => (
              <TableRow
                key={i}
                cells={row.map((cell) => ({
                  contents: cell.contents,
                  width: cell.width,
                  paddingX: cell.paddingX,
                  paddingY: cell.paddingY,
                }))} />
            )) :
          <tr className="bg-light">
            <td colSpan={columns.length} className="border-r border-t border-light text-[#666699] px-1 py-3">
              <i>No data to display</i>
            </td>
          </tr>
        }
      </>
    );
    setRowsRendered(fragment);
  }

  return (
    <>
      {(includeControl || includeSearch) &&
        <TableControl
          control={control}
          controlWidth={controlWidth}
          includeControl={includeControl}
          includeSearch={includeSearch}
          onSearch={onSearch} />
      }

      <table className="border border-light w-full">
        <thead>
          <TableHeader headers={headers} onSort={onSort} />
        </thead>
        <tbody>{rowsRendered}</tbody>
      </table>

      <div className="flex flex-col">
        <div className="flex items-center mb-2">
          <Button
            variant="secondary"
            size="sm"
            square={true}
            disabled={page === 1}
            onClick={() => page > 1 && paginate(page - 1)}>
              <KeyboardArrowLeftIcon />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            square={true}
            disabled={page === totalPages}
            onClick={() => page < totalPages && paginate(page + 1)}>
              <KeyboardArrowRightIcon />
          </Button>
          <span className="ml-2">
            Page {page} of {totalPages || 1}
          </span>
        </div>
        <span>
          {totalPages &&
            `${(page - 1) * paginationPer + 1} - ${Math.min(
              rowsFiltered.length,
              page * paginationPer
            )} of `
          }
          {rowsFiltered.length} item{rowsFiltered.length === 1 ? "" : "s"}
        </span>
      </div>
    </>
  );
};

export default Table;
