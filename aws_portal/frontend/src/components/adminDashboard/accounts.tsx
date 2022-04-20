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
        name: "Name",
        searchable: false,
        sortable: false,
        width: 20
      },
      {
        name: "Email",
        searchable: false,
        sortable: false,
        width: 35
      },
      {
        name: "Created On",
        searchable: false,
        sortable: false,
        width: 15
      },
      {
        name: "Last Login",
        searchable: false,
        sortable: false,
        width: 15
      },
      {
        name: "",
        searchable: false,
        sortable: false,
        width: 15
      }
    ]
  };

  getData = () => {
    return [
      [
        {
          contents: <div className="flex-center">John Smith</div>,
          name: "Name",
          searchValue: "",
          sortValue: "",
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "",
          sortValue: "",
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          name: "",
          searchValue: "",
          sortValue: "",
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith</div>,
          name: "Name",
          searchValue: "",
          sortValue: "",
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "",
          sortValue: "",
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          name: "",
          searchValue: "",
          sortValue: "",
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith</div>,
          name: "Name",
          searchValue: "",
          sortValue: "",
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "",
          sortValue: "",
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          name: "",
          searchValue: "",
          sortValue: "",
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith</div>,
          name: "Name",
          searchValue: "",
          sortValue: "",
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "",
          sortValue: "",
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          name: "",
          searchValue: "",
          sortValue: "",
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith</div>,
          name: "Name",
          searchValue: "",
          sortValue: "",
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "",
          sortValue: "",
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          name: "",
          searchValue: "",
          sortValue: "",
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith</div>,
          name: "Name",
          searchValue: "",
          sortValue: "",
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "",
          sortValue: "",
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          sortValue: "",
          width: 15
        },
        {
          contents: (
            <div className="flex-center table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          name: "",
          searchValue: "",
          sortValue: "",
          width: 15
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
            control={
              <button className="button-primary">
                Create&nbsp;<b>+</b>
              </button>
            }
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
