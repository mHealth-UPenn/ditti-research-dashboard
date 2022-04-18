import * as React from "react";
import { Component } from "react";
import Table from "../table/table";
import Navbar from "./navbar";

interface AccountsProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface AccountsState {
  columns: {
    name: string;
    searchable: boolean;
    sortable: boolean;
    width: number;
  }[];
}

class Accounts extends React.Component<AccountsProps, AccountsState> {
  state = {
    columns: [
      {
        name: "a",
        searchable: false,
        sortable: false,
        width: 10
      },
      {
        name: "b",
        searchable: false,
        sortable: false,
        width: 10
      },
      {
        name: "c",
        searchable: false,
        sortable: false,
        width: 10
      }
    ]
  };

  getData = () => {
    return [
      [
        {
          contents: <div>1</div>,
          name: "1",
          searchValue: "",
          sortValue: "",
          width: 10
        },
        {
          contents: <div>2</div>,
          name: "2",
          searchValue: "",
          sortValue: "",
          width: 10
        },
        {
          contents: <div>3</div>,
          name: "3",
          searchValue: "",
          sortValue: "",
          width: 10
        }
      ]
    ];
  };

  render() {
    const { handleClick } = this.props;
    const { columns } = this.state;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Accounts" />
        <div className="page-content bg-white">
          <Table
            columns={columns}
            control={<div>Control</div>}
            controlWidth={15}
            data={this.getData()}
            includeControl={true}
            includeSearch={true}
            paginationPer={20}
            sortDefault=""
          />
        </div>
      </div>
    );
  }
}

export default Accounts;
