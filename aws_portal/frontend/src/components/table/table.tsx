import * as React from "react";
import { Component } from "react";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TablePagination from "./tablePagination";
import TableRow from "./tableRow";

interface TableProps {
  columns: {
    name: string;
    searchable: boolean;
    sortable: boolean;
  }[];
  columnWidths: {
    name: string;
    width: number;
  }[];
  control: React.ReactElement;
  controlWidth: number;
  data: {
    contents: React.ReactElement;
    name: string;
    searchValue: string;
    sortValue: string;
  }[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}

interface TableState {
  page: number;
  searchText: string;
  sortBy: string;
}

class Table extends React.Component<TableProps, TableState> {
  onSearch = (text: string) => {
    console.log(text);
  };

  onSort = (name: string, ascending: boolean) => {
    console.log(name, ascending);
  };

  paginate = (page: number) => {
    console.log(page);
  };

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

    return (
      <div className="table-container">
        includeControl || includeSearch ?
        <TableControl
          control={control}
          controlWidth={controlWidth}
          includeControl={includeControl}
          includeSearch={includeSearch}
          onSearch={this.onSearch}
        />
        <table>
          <TableHeader
            columns={columns}
            onSort={this.onSort}
            sortDefault={sortDefault}
          />
          {data.map((row) => (
            <TableRow data={row} />
          ))}
        </table>
        <TablePagination
          onClick={this.paginate}
          paginationPer={paginationPer}
          totalRows={data.length}
        />
      </div>
    );
  }
}

export default Table;
