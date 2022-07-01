import * as React from "react";
import { Component } from "react";
import { ResponseBody, Role, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import RolesEdit from "./rolesEdit";
import { SmallLoader } from "../loader";

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
    const create = getAccess(1, "Create", "Roles")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    const edit = getAccess(1, "Edit", "Roles")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    const archive = getAccess(1, "Archive", "Roles")
      .then(() => this.setState({ canArchive: true }))
      .catch(() => this.setState({ canArchive: false }));

    const roles = makeRequest("/admin/role?app=1").then((roles) =>
      this.setState({ roles })
    );

    Promise.all([create, edit, archive, roles]).then(() =>
      this.setState({ loading: false })
    );
  }

  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, canArchive, roles } = this.state;

    return roles.map((r: Role) => {
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

  delete = (id: number): void => {
    const body = { app: 1, id };
    const opts = { method: "POST", body: JSON.stringify(body) };
    const msg = "Are you sure you want to archive this role?";

    if (confirm(msg))
      makeRequest("/admin/role/archive", opts)
        .then(this.handleSuccess)
        .catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    const { flashMessage } = this.props;
    flashMessage(<span>{res.msg}</span>, "success");
  };

  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

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
