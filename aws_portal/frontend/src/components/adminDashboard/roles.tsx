import * as React from "react";
import { Component } from "react";
import { Role, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import RolesEdit from "./rolesEdit";
import { SmallLoader } from "../loader";

interface RolesState {
  roles: Role[];
  columns: Column[];
  loading: boolean;
}

class Roles extends React.Component<ViewProps, RolesState> {
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
    const { flashMessage, goBack, handleClick } = this.props;

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
                  handleClick(
                    ["Edit", name],
                    <RolesEdit
                      roleId={id}
                      flashMessage={flashMessage}
                      goBack={goBack}
                      handleClick={handleClick}
                    />
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
    const { flashMessage, goBack, handleClick } = this.props;
    const { columns, loading } = this.state;

    const tableControl = (
      <button
        className="button-primary"
        onClick={() =>
          handleClick(
            ["Create"],
            <RolesEdit
              roleId={0}
              flashMessage={flashMessage}
              goBack={goBack}
              handleClick={handleClick}
            />
          )
        }
      >
        Create&nbsp;<b>+</b>
      </button>
    );

    return (
      <div className="page-container">
        <Navbar
          active="Roles"
          flashMessage={flashMessage}
          goBack={goBack}
          handleClick={handleClick}
        />
        <div className="page-content bg-white">
          {loading ? (
            <SmallLoader />
          ) : (
            <Table
              columns={columns}
              control={tableControl}
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
    );
  }
}

export default Roles;
