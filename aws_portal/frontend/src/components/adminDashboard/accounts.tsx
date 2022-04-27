import * as React from "react";
import { Component } from "react";
import Table from "../table/table";
import Navbar from "./navbar";

const data = [
  {
    name: "John Smith1",
    email: "john.smith1@pennmedicine.upenn.edu",
    createdOn: new Date("Jan 1, 2022"),
    lastLogin: 21
  },
  {
    name: "John Smith2",
    email: "john.smith2@pennmedicine.upenn.edu",
    createdOn: new Date("Feb 6, 2022"),
    lastLogin: 1
  },
  {
    name: "John Smith3",
    email: "john.smith3@pennmedicine.upenn.edu",
    createdOn: new Date("Apr 2, 2022"),
    lastLogin: 354
  },
  {
    name: "Jane Doe2",
    email: "jane.doe2@pennmedicine.upenn.edu",
    createdOn: new Date("Jan 1, 2022"),
    lastLogin: 0
  },
  {
    name: "Jane Doe3",
    email: "jane.doe3@pennmedicine.upenn.edu",
    createdOn: new Date("Dec 31, 2021"),
    lastLogin: 12
  },
  {
    name: "Jane Doe4",
    email: "jane.doe4@pennmedicine.upenn.edu",
    createdOn: new Date("Oct 1, 2021"),
    lastLogin: 44
  }
];

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
    sortable: boolean;
    width: number;
  }[];
}

class Accounts extends React.Component<AccountsProps, AccountsState> {
  state = {
    columns: [
      {
        name: "Name",
        searchable: true,
        sortable: true,
        width: 25
      },
      {
        name: "Email",
        searchable: true,
        sortable: true,
        width: 35
      },
      {
        name: "Created On",
        searchable: false,
        sortable: true,
        width: 15
      },
      {
        name: "Last Login",
        searchable: false,
        sortable: true,
        width: 15
      },
      {
        name: "",
        searchable: false,
        sortable: false,
        width: 10
      }
    ]
  };

  getData = () => {
    const pad = Math.max(...data.map((row) => String(row.lastLogin).length));
    return data.map((row) => {
      const { createdOn, email, lastLogin, name } = row;

      return [
        {
          contents: (
            <div className="flex-center table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <div className="flex-center table-data">
              <span>{email}</span>
            </div>
          ),
          searchValue: email,
          sortValue: email
        },
        {
          contents: (
            <div className="flex-center table-data">
              <span>{createdOn.toDateString()}</span>
            </div>
          ),
          searchValue: "",
          sortValue: String(createdOn.getTime())
        },
        {
          contents: (
            <div className="flex-center table-data">
              <span>
                {lastLogin
                  ? `${lastLogin} day${lastLogin === 1 ? "" : "s"} ago`
                  : "Today"}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: String(lastLogin).padStart(pad, "0")
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
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
            control={
              <button className="button-primary">
                Create&nbsp;<b>+</b>
              </button>
            }
            controlWidth={10}
            data={this.getData()}
            includeControl={true}
            includeSearch={true}
            paginationPer={2}
            sortDefault=""
          />
        </div>
      </div>
    );
  }
}

export default Accounts;
