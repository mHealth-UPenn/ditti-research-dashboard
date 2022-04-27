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
        name: "Name",
        searchable: true,
        sortable: true,
        width: 20
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
        width: 15
      }
    ]
  };

  getData = () => {
    return [
      [
        {
          contents: <div className="flex-center">John Smith1</div>,
          searchValue: "John Smith1",
          sortValue: "John Smith1"
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          searchValue: "john.smith@pennmedicine.upenn.edu",
          sortValue: "john.smith@pennmedicine.upenn.edu"
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          searchValue: "",
          sortValue: ""
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          searchValue: "",
          sortValue: ""
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
      ],
      [
        {
          contents: <div className="flex-center">John Smith2</div>,
          searchValue: "John Smith2",
          sortValue: "John Smith2"
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          searchValue: "john.smith@pennmedicine.upenn.edu",
          sortValue: "john.smith@pennmedicine.upenn.edu"
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          searchValue: "",
          sortValue: ""
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          searchValue: "",
          sortValue: ""
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
      ],
      [
        {
          contents: <div className="flex-center">John Smith3</div>,
          searchValue: "John Smith3",
          sortValue: "John Smith3"
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          searchValue: "john.smith@pennmedicine.upenn.edu",
          sortValue: "john.smith@pennmedicine.upenn.edu"
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          searchValue: "",
          sortValue: ""
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          searchValue: "",
          sortValue: ""
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
      ],
      [
        {
          contents: <div className="flex-center">Jane Smith2</div>,
          searchValue: "Jane Smith2",
          sortValue: "Jane Smith2"
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          searchValue: "john.smith@pennmedicine.upenn.edu",
          sortValue: "john.smith@pennmedicine.upenn.edu"
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          searchValue: "",
          sortValue: ""
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          searchValue: "",
          sortValue: ""
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
      ],
      [
        {
          contents: <div className="flex-center">Jane Smith3</div>,
          searchValue: "Jane Smith3",
          sortValue: "Jane Smith3"
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          searchValue: "john.smith@pennmedicine.upenn.edu",
          sortValue: "john.smith@pennmedicine.upenn.edu"
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          searchValue: "",
          sortValue: ""
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          searchValue: "",
          sortValue: ""
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
      ],
      [
        {
          contents: <div className="flex-center">Jane Smith4</div>,
          searchValue: "Jane Smith4",
          sortValue: "Jane Smith4"
        },
        {
          contents: (
            <div className="flex-center">john.smith@pennmedicine.upenn.edu</div>
          ),
          searchValue: "john.smith@pennmedicine.upenn.edu",
          sortValue: "john.smith@pennmedicine.upenn.edu"
        },
        {
          contents: <div className="flex-center">Jan 1, 2022</div>,
          searchValue: "",
          sortValue: ""
        },
        {
          contents: <div className="flex-center">1 day ago</div>,
          searchValue: "",
          sortValue: ""
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
