import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";
import Table, { Column, TableData } from "../table/table";
import AccessGroupsEdit from "./accessGroupsEdit";
import { AccessGroup, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";

interface AccessGroupsState {
  accessGroups: AccessGroup[];
  columns: Column[];
  loading: boolean;
}

class AccessGroups extends React.Component<ViewProps, AccessGroupsState> {
  state = {
    accessGroups: [],
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
        name: "Permissions",
        searchable: false,
        sortable: false,
        width: 50
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
    makeRequest("/admin/access-group?app=1").then((accessGroups) =>
      this.setState({ accessGroups, loading: false })
    );
  }

  getData = (): TableData[][] => {
    const handleClick = this.props.handleClick
      ? this.props.handleClick
      : () => null;

    return this.state.accessGroups.map((ag: AccessGroup) => {
      const { app, id, name, permissions } = ag;

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
              <span>{app.name}</span>
            </div>
          ),
          searchValue: app.name,
          sortValue: app.name
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {permissions
                  .map(
                    (p) =>
                      (p.action == "*" ? "All Actions" : p.action) +
                      " - " +
                      (p.resource == "*" ? "All Resources" : p.resource)
                  )
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
                    <AccessGroupsEdit accessGroupId={id} />,
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
    const handleClick = this.props.handleClick
      ? this.props.handleClick
      : () => null;

    const { columns, loading } = this.state;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Access Groups" />
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

export default AccessGroups;
