import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";
import Table, { Column, TableData } from "../table/table";
import AccessGroupsEdit from "./accessGroupsEdit";
import { AccessGroup, ResponseBody, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";

interface AccessGroupsState {
  canCreate: boolean;
  canEdit: boolean;
  canArchive: boolean;
  accessGroups: AccessGroup[];
  columns: Column[];
  loading: boolean;
}

class AccessGroups extends React.Component<ViewProps, AccessGroupsState> {
  state = {
    canCreate: false,
    canEdit: false,
    canArchive: false,
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
    const create = getAccess(1, "Create", "Access Groups")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    const edit = getAccess(1, "Edit", "Access Groups")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    const archive = getAccess(1, "Archive", "Access Groups")
      .then(() => this.setState({ canArchive: true }))
      .catch(() => this.setState({ canArchive: false }));

    const accessGroups = makeRequest("/admin/access-group?app=1").then(
      (accessGroups) => this.setState({ accessGroups })
    );

    Promise.all([create, edit, archive, accessGroups]).then(() =>
      this.setState({ loading: false })
    );
  }

  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, canArchive, accessGroups } = this.state;

    return accessGroups.map((ag: AccessGroup) => {
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
              {canEdit ? (
                <button
                  className="button-secondary"
                  onClick={() =>
                    handleClick(
                      ["Edit", name],
                      <AccessGroupsEdit
                        accessGroupId={id}
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
    makeRequest("/admin/access-group/archive", opts)
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
            <AccessGroupsEdit
              accessGroupId={0}
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
          handleClick={handleClick}
          active="Access Groups"
          flashMessage={flashMessage}
          goBack={goBack}
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

export default AccessGroups;
