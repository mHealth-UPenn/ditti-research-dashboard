import * as React from "react";
import { renderToString } from "react-dom/server";
import { Component } from "react";
import TableControl from "./tableControl";
import TableHeader from "./tableHeader";
import TableRow from "./tableRow";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import "./table.css";

interface TableData {
  contents: React.ReactElement;
  name: string;
  searchable: boolean;
  searchValue: string;
  sortable: boolean;
  sortValue: string;
  width: number;
}

interface TableProps {
  columns: {
    name: string;
    sortable: boolean;
    width: number;
  }[];
  control: React.ReactElement;
  controlWidth: number;
  data: TableData[][];
  includeControl: boolean;
  includeSearch: boolean;
  paginationPer: number;
  sortDefault: string;
}

interface TableState {
  page: number;
  renderedData: TableData[][];
  renderedRows: React.ReactElement;
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
      renderedData: data,
      renderedRows: <React.Fragment />,
      sortBy: "",
      totalPages: totalPages
    };
  }

  componentDidMount() {
    const { renderedData } = this.state;
    this.renderRows(1, renderedData);
  }

  onSearch = (text: string) => {
    const { data, paginationPer } = this.props;
    const renderedData = data.filter((row) =>
      row.some(
        (cell) =>
          cell.searchable &&
          cell.searchValue.toLowerCase().includes(text.toLowerCase())
      )
    );

    const totalPages = Math.ceil(renderedData.length / paginationPer);
    this.setState({ page: 1, renderedData, totalPages });
    this.renderRows(1, renderedData);
  };

  onSort = (name: string, ascending: boolean) => {
    console.log(name, ascending);
  };

  paginate = (page: number) => {
    const { renderedData } = this.state;

    this.renderRows(page, renderedData);
    this.setState({ page });
  };

  renderRows(page: number, data: TableData[][]) {
    const { paginationPer } = this.props;

    const renderedRows = (
      <React.Fragment>
        {data
          .slice((page - 1) * paginationPer, page * paginationPer)
          .map((row) => (
            <TableRow data={row} />
          ))}
      </React.Fragment>
    );

    this.setState({ renderedRows });
  }

  render() {
    const {
      columns,
      control,
      controlWidth,
      includeControl,
      includeSearch,
      paginationPer,
      sortDefault
    } = this.props;

    const { page, renderedData, renderedRows, totalPages } = this.state;

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
            {renderedData.length} items
          </span>
        </div>
      </div>
    );
  }
}

export default Table;
