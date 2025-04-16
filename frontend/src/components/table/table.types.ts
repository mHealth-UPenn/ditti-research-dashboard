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

/**
 * The props for the TableRow component.
 * @property cells - The row's cells.
 */
export interface TableRowProps {
  cells: {
    contents: React.ReactElement | string;
    width: number;
    paddingX?: number;
    paddingY?: number;
  }[];
}

/**
 * The props for the TableHeader component.
 * @property headers - The table's headers.
 * @property onSort - The callback function when the user sorts.
 */
export interface TableHeaderProps {
  headers: Header[];
  onSort: (name: string, ascending: 0 | 1) => void;
}

/**
 * The props for the TableControl component.
 * @property control - The control to display in the table.
 * @property controlWidth - The width of the control.
 * @property includeControl - Whether to include the control.
 * @property includeSearch - Whether to include the search.
 * @property onSearch - The callback function when the user searches.
 */
export interface TableControlProps {
  control: React.ReactElement;
  controlWidth: number;
  includeControl: boolean;
  includeSearch: boolean;
  onSearch: (text: string) => void;
}

/**
 * The props for the TableCell component.
 * @property width - The width of the cell.
 * @property paddingX - The padding of the cell.
 * @property paddingY - The padding of the cell.
 */
export interface TableCellProps {
  width: number;
  paddingX?: number;
  paddingY?: number;
}

/**
 * The props for table columns.
 * @property name - The name to display in the column header.
 * @property searchable - Whether the column is searchable.
 * @property sortable - Whether the column is sortable.
 * @property width - The column's display width.
 */
export interface Column {
  name: string;
  searchable: boolean;
  sortable: boolean;
  width: number;
}

/**
 * The props for table headers.
 * @property ascending - Whether the header is unsorted, descending, or ascending.
 * @property name - The header's name to display.
 * @property sortable - Whether the header's column is sortable.
 * @property width - The column's display width.
 */
export interface Header {
  ascending: -1 | 0 | 1;
  name: string;
  sortable: boolean;
  width: number;
}

/**
 * The props for table data.
 * @property contents - The contents of the cell to render.
 * @property sortValue - The value to sort the cell on.
 * @property searchValue - The value used for searching.
 * @property paddingX - The padding of the cell.
 * @property paddingY - The padding of the cell.
 */
export interface TableData {
  contents: React.ReactElement | string;
  sortValue?: string | number;
  searchValue?: string;
  paddingX?: number;
  paddingY?: number;
}

/**
 * A table cell as it used for rendering purposes.
 * @property contents - The contents of the cell to render.
 * @property searchable - Whether the cell is in a searchable column.
 * @property searchValue - The value used for searching.
 * @property sortable - Whether the cell is in a searchable column.
 * @property width - The column's display width.
 */
export interface Cell {
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
 * The props for the Table component.
 * @property columns - The table columns.
 * @property control - The control element (e.g., a create button).
 * @property controlWidth - The control's display width.
 * @property data - An array of rows that are arrays of table cells.
 * @property includeControl - Whether to show the control element.
 * @property includeSearch - Whether to show the search bar.
 * @property paginationPer - The number of rows to show per page.
 * @property sortDefault - The name of the default sort column.
 */
export interface TableProps {
  columns: Column[];
  control: React.ReactElement;
  controlWidth: number;
  data: TableData[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}
