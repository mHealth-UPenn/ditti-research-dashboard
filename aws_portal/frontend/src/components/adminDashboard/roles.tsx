import * as React from "react";
import { Component } from "react";
import Table from "../table/table";
import Navbar from "./navbar";
import RolesEdit from "./rolesEdit";
import { rolesRaw } from "./studiesEdit";

interface RolesProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface RolesState {
  columns: {
    name: string;
    sortable: boolean;
    width: number;
  }[];
}

class Roles extends React.Component<RolesProps, RolesState> {
  state = {
    columns: [
      {
        name: "Name",
        searchable: true,
        sortable: true,
        width: 15
      },
      {
        name: "Permissions",
        searchable: false,
        sortable: false,
        width: 75
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
    return rolesRaw.map((role) => {
      const { name, permissions } = role;

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
              <span>
                {permissions
                  .map((p) => p.action + " - " + p.resource)
                  .join(", ")}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: ""
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
        <Navbar handleClick={handleClick} active="Roles" />
        <div className="page-content bg-white">
          <Table
            columns={columns}
            control={
              <button
                className="button-primary"
                onClick={() =>
                  handleClick(["Create"], <RolesEdit roleId={0} />, false)
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

export default Roles;
