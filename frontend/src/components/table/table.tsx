/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { useState } from "react";
import { TableControl } from "./tableControl";
import { TableHeader } from "./tableHeader";
import { TableRow } from "./tableRow";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import { Button } from "../buttons/button";
import { Header, Cell, TableProps } from "./table.types";

export const Table = ({
  columns,
  control,
  controlWidth,
  data,
  includeControl,
  includeSearch,
  paginationPer,
  sortDefault,
}: TableProps) => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState<string | null>(null);
  const [sort, setSort] = useState<{ name: string; ascending: 0 | 1 } | null>(
    null
  );

  const onSort = (name: string, ascending: 0 | 1) => {
    setSort({ name, ascending });
  };

  const headers: Header[] = columns.map((c) => ({
    ascending: sort
      ? sort.name === c.name
        ? sort.ascending
        : -1
      : sortDefault === c.name
        ? 1
        : -1,
    name: c.name,
    sortable: c.sortable,
    width: c.width,
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
  );

  if (search) {
    rows = rows.filter((row) =>
      row.some((cell) => cell.searchValue.includes(search))
    );
  }

  if (sort) {
    let index = 0;
    headers.forEach((header, i) => {
      const isSortHeader = header.name === sort.name;
      if (isSortHeader) index = i;
    });

    rows = rows.sort((a, b) => {
      const aValue = a[index].sortValue;
      const bValue = b[index].sortValue;

      if (aValue < bValue) return sort.ascending ? -1 : 1;
      else if (aValue > bValue) return sort.ascending ? 1 : -1;
      else return 0;
    });
  }

  const totalPages = Math.ceil(rows.length / paginationPer);

  return (
    <>
      {(includeControl || includeSearch) && (
        <TableControl
          control={control}
          controlWidth={controlWidth}
          includeControl={includeControl}
          includeSearch={includeSearch}
          onSearch={setSearch}
        />
      )}

      <table className="w-full border border-light">
        <thead>
          <TableHeader headers={headers} onSort={onSort} />
        </thead>
        <tbody>
          <>
            {rows.length ? (
              rows
                .slice((page - 1) * paginationPer, page * paginationPer)
                .map((row, i) => (
                  <TableRow
                    key={i}
                    cells={row.map((cell) => ({
                      contents: cell.contents,
                      width: cell.width,
                      paddingX: cell.paddingX,
                      paddingY: cell.paddingY,
                    }))}
                  />
                ))
            ) : (
              <tr className="bg-extra-light">
                <td
                  colSpan={columns.length}
                  className="border-r border-t border-light px-1 py-3 text-link"
                >
                  <i>No data to display</i>
                </td>
              </tr>
            )}
          </>
        </tbody>
      </table>

      <div className="flex flex-col">
        <div className="mb-2 flex items-center">
          <Button
            variant="secondary"
            size="sm"
            square={true}
            disabled={page === 1}
            onClick={() => page > 1 && setPage(page - 1)}
          >
            <KeyboardArrowLeftIcon />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            square={true}
            disabled={!rows.length || page === totalPages}
            onClick={() => page < totalPages && setPage(page + 1)}
          >
            <KeyboardArrowRightIcon />
          </Button>
          <span className="ml-2">
            Page {page} of {totalPages || 1}
          </span>
        </div>
        <span>
          {!!rows.length &&
            totalPages &&
            `${(page - 1) * paginationPer + 1} - ${Math.min(
              rows.length,
              page * paginationPer
            )} of `}
          {rows.length} item{rows.length === 1 ? "" : "s"}
        </span>
      </div>
    </>
  );
};
