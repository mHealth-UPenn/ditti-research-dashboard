import React, { useState } from "react";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TableRow from "./tableRow";
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
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
  contents: React.ReactElement | string;
  sortValue?: string | number;
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
  contents: React.ReactElement | string;
  searchable: boolean;
  searchValue: string;
  sortable: boolean;
  sortValue: string | number;
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
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState<string | null>(null);
  const [sort, setSort] = useState<{ name: string; ascending: 0 | 1 } | null>(null);

  const onSort = (name: string, ascending: 0 | 1) => {
    setSort({ name, ascending });
  }

  const headers: Header[] = columns.map((c) => ({
    ascending: (sort ? (sort.name === c.name ? sort.ascending : -1) : (sortDefault === c.name ? 1 : -1)),
    name: c.name,
    sortable: c.sortable,
    width: c.width
  }));

  let rows: Cell[][] = data.map((row) =>
    row.map((cell, i) => ({
      contents: cell.contents,
      searchable: columns[i].searchable,
      searchValue: cell.searchValue || "",
      sortable: columns[i].sortable,
      sortValue: cell.sortValue || "",
      width: columns[i].width,
      paddingX: cell.paddingX,
      paddingY: cell.paddingY,
    }))
  )

  if (search) {
    rows = rows.filter(
      row => row.some(cell => cell.searchValue.includes(search))
    );
  }

  if (sort) {
    let index = 0;
    headers.forEach((header, i) => {
      const isSortHeader = header.name === (sort ? sort.name : sortDefault);
      if (isSortHeader) index = i;
      return {
        ...header,
        ascending: isSortHeader ? sort.ascending : -1
      }
    });

    rows = rows.sort((a, b) => {
      if (a[index].sortValue < b[index].sortValue) return sort.ascending ? -1 : 1;
      else if (a[index].sortValue > b[index].sortValue) return sort.ascending ? 1 : -1;
      else return 0;
    });
  }

  const totalPages = Math.ceil(rows.length / paginationPer);

  return (
    <>
      {(includeControl || includeSearch) &&
        <TableControl
          control={control}
          controlWidth={controlWidth}
          includeControl={includeControl}
          includeSearch={includeSearch}
          onSearch={setSearch} />
      }

      <table className="border border-light w-full">
        <thead>
          <TableHeader headers={headers} onSort={onSort} />
        </thead>
        <tbody>
          <>
            {rows.length ?
              rows.slice((page - 1) * paginationPer, page * paginationPer)
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
              <tr className="bg-extra-light">
                <td colSpan={columns.length} className="border-r border-t border-light text-link px-1 py-3">
                  <i>No data to display</i>
                </td>
              </tr>
            }
          </>
        </tbody>
      </table>

      <div className="flex flex-col">
        <div className="flex items-center mb-2">
          <Button
            variant="secondary"
            size="sm"
            square={true}
            disabled={page === 1}
            onClick={() => page > 1 && setPage(page - 1)}>
              <KeyboardArrowLeftIcon />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            square={true}
            disabled={!rows.length || page === totalPages}
            onClick={() => page < totalPages && setPage(page + 1)}>
              <KeyboardArrowRightIcon />
          </Button>
          <span className="ml-2">
            Page {page} of {totalPages || 1}
          </span>
        </div>
        <span>
          {(!!rows.length && totalPages) &&
            `${(page - 1) * paginationPer + 1} - ${Math.min(
              rows.length,
              page * paginationPer
            )} of `
          }
          {rows.length} item{rows.length === 1 ? "" : "s"}
        </span>
      </div>
    </>
  );
};

export default Table;
