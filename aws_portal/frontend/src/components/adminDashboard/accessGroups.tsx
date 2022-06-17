import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";
import Table from "../table/table";
import AccessGroupsEdit from "./accessGroupsEdit";

const data = [
  {
    app: "Ditti App",
    name: "Ditti App Staff",
    roles: ["Coordinator", "Manager"],
    studies: ["MSBI", "ART OSA"]
  },
  {
    app: "Ditti App",
    name: "Ditti App Admins",
    roles: ["Admin", "Super Admin"],
    studies: ["MSBI", "ART OSA"]
  },
  {
    app: "Admin Dashboard",
    name: "Admins",
    roles: ["Admin", "Super Admin"],
    studies: []
  }
];

interface AccessGroupsProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface AccessGroupsState {
  columns: {
    name: string;
    sortable: boolean;
    width: number;
  }[];
}

class AccessGroups extends React.Component<
  AccessGroupsProps,
  AccessGroupsState
> {
  state = {
    columns: [
      {
        name: "Name",
        searchable: true,
        sortable: true,
        width: 20
      },
      {
        name: "App",
        searchable: true,
        sortable: true,
        width: 20
      },
      {
        name: "Roles",
        searchable: false,
        sortable: false,
        width: 25
      },
      {
        name: "Studies",
        searchable: true,
        sortable: false,
        width: 25
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
    return data.map((row) => {
      const { app, name, roles, studies } = row;

      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{app}</span>
            </div>
          ),
          searchValue: app,
          sortValue: app
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{roles.join(", ")}</span>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{studies.join(", ")}</span>
            </div>
          ),
          searchValue: studies.join(", "),
          sortValue: studies.join(", ")
        },
        {
          contents: (
            <div className="flex-left table-control">
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
        <Navbar handleClick={handleClick} active="Access Groups" />
        <div className="page-content bg-white">
          <Table
            columns={columns}
            control={
              <button
                className="button-primary"
                onClick={() =>
                  handleClick(
                    ["Create"],
                    <AccessGroupsEdit accessGroupId={0} />,
                    false
                  )
                }
              >
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

export default AccessGroups;
