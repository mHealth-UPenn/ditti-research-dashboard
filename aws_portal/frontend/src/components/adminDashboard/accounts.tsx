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
    sortable: boolean;
    width: number;
  }[];
}

class Accounts extends React.Component<AccountsProps, AccountsState> {
  state = {
    columns: [
      {
        ascending: false,
        descending: false,
        name: "Name",
        sortable: true,
        width: 20
      },
      {
        ascending: false,
        descending: false,
        name: "Email",
        sortable: true,
        width: 35
      },
      {
        ascending: false,
        descending: false,
        name: "Created On",
        sortable: true,
        width: 15
      },
      {
        ascending: false,
        descending: false,
        name: "Last Login",
        sortable: true,
        width: 15
      },
      {
        ascending: false,
        descending: false,
        name: "",
        sortable: false,
        width: 15
      }
    ]
  };

  getData = () => {
    return [
      [
        {
          contents: <div className="flex-center">John Smith1</div>,
          name: "Name",
          searchValue: "John Smith1",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "john.smith@pennmedicine.upenn.edu",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
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
          searchable: false,
          sortValue: "",
          sortable: false,
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith2</div>,
          name: "Name",
          searchValue: "John Smith2",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "john.smith@pennmedicine.upenn.edu",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
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
          searchable: false,
          sortValue: "",
          sortable: false,
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">John Smith3</div>,
          name: "Name",
          searchValue: "John Smith3",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "john.smith@pennmedicine.upenn.edu",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
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
          searchable: false,
          sortValue: "",
          sortable: false,
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">Jane Smith2</div>,
          name: "Name",
          searchValue: "Jane Smith2",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "john.smith@pennmedicine.upenn.edu",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
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
          searchable: false,
          sortValue: "",
          sortable: false,
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">Jane Smith3</div>,
          name: "Name",
          searchValue: "Jane Smith3",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "john.smith@pennmedicine.upenn.edu",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
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
          searchable: false,
          sortValue: "",
          sortable: false,
          width: 15
        }
      ],
      [
        {
          contents: <div className="flex-center">Jane Smith4</div>,
          name: "Name",
          searchValue: "Jane Smith4",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 20
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          name: "Email",
          searchValue: "john.smith@pennmedicine.upenn.edu",
          searchable: true,
          sortValue: "",
          sortable: true,
          width: 35
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          name: "Created On",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
          width: 15
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          name: "Last Login",
          searchValue: "",
          searchable: false,
          sortValue: "",
          sortable: true,
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
          searchable: false,
          sortValue: "",
          sortable: false,
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
            paginationPer={2}
            sortDefault=""
          />
        </div>
      </div>
    );
  }
}

export default Accounts;
