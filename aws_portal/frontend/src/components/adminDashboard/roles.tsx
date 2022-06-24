import * as React from "react";
import { Component } from "react";
import { Role } from "../../interfaces";
import { makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import RolesEdit from "./rolesEdit";
import { SmallLoader } from "../loader";

interface RolesProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface RolesState {
  roles: Role[];
  columns: Column[];
  loading: boolean;
}

class Roles extends React.Component<RolesProps, RolesState> {
  state = {
    roles: [],
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
    ],
    loading: true
  };

  async componentDidMount() {
    makeRequest("/admin/role?app=1").then((roles) =>
      this.setState({ roles, loading: false })
    );
  }

  getData = (): TableData[][] => {
    return this.state.roles.map((r: Role) => {
      const { id, name, permissions } = r;

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
              <button
                className="button-secondary"
                onClick={() =>
                  this.props.handleClick(
                    ["Edit", name],
                    <RolesEdit roleId={id} />,
                    false
                  )
                }
              >
                Edit
              </button>
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
    const { columns, loading } = this.state;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Roles" />
        <div className="page-content bg-white">
          <div style={{ position: "relative", height: "100%", width: "100%" }}>
            {loading ? (
              <SmallLoader />
            ) : (
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
                paginationPer={10}
                sortDefault=""
              />
            )}
          </div>
        </div>
      </div>
    );
  }
}

export default Roles;
