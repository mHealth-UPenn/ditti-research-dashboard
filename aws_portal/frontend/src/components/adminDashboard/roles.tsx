import * as React from "react";
import { Component } from "react";
import { ResponseBody, Role, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import RolesEdit from "./rolesEdit";
import { SmallLoader } from "../loader";

/**
 * canCreate: whether the user has permissions to create
 * canEdit: whether the user has permissions to edit
 * canArchive: whether the user permissions to archive
 * roles: an array of rows to display in the table
 * columns: an array of columns to display in the table
 * loading: whether to display the loading screen
 */
interface RolesState {
  canCreate: boolean;
  canEdit: boolean;
  canArchive: boolean;
  roles: Role[];
  columns: Column[];
  loading: boolean;
}

class Roles extends React.Component<ViewProps, RolesState> {
  state = {
    canCreate: false,
    canEdit: false,
    canArchive: false,
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

    // check whether the user has permission to create
    const create = getAccess(1, "Create", "Roles")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    // check whether the user has permissions to edit
    const edit = getAccess(1, "Edit", "Roles")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    // check whether the user has permissions to archive
    const archive = getAccess(1, "Archive", "Roles")
      .then(() => this.setState({ canArchive: true }))
      .catch(() => this.setState({ canArchive: false }));

    // get the table's data
    const roles = makeRequest("/admin/role?app=1").then((roles) =>
      this.setState({ roles })
    );

    // when all requests are complete, hide the loading screen
    Promise.all([create, edit, archive, roles]).then(() =>
      this.setState({ loading: false })
    );
  }

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, canArchive, roles } = this.state;

    // iterate over the table's rows
    return roles.map((r: Role) => {
      const { id, name, permissions } = r;

      // map each row to a set of cells for each table column
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
                  .map((p) => {
                    const action = p.action == "*" ? "All Actions" : p.action;
                    const resource =
                      p.resource == "*" ? "All Resources" : p.resource;
                    return action + " - " + resource;
                  })
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
              {canEdit ? (
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
              ) : null}
              {canArchive ? (
                <button
                  className="button-danger"
                  onClick={() => this.delete(id)}
                >
                  Archive
                </button>
              ) : null}
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  delete = (id: number): void => {

    // prepare the request
    const body = { app: 1, id };  // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    // confirm deletion
    const msg = "Are you sure you want to archive this role?";

    if (confirm(msg))
      makeRequest("/admin/role/archive", opts)
        .then(this.handleSuccess)
        .catch(this.handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  handleSuccess = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    // show the loading screen
    this.setState({ loading: true });
    flashMessage(<span>{res.msg}</span>, "success");

    // refresh the table's data
    makeRequest("/admin/role?app=1").then((roles) =>
      this.setState({ roles, loading: false })
    );
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    // flash the message returned from the endpoint or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  render() {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canCreate, columns, loading } = this.state;

    // if the user has permission to create, show the create button
    const tableControl = canCreate ? (
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
    ) : (
      <React.Fragment />
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
