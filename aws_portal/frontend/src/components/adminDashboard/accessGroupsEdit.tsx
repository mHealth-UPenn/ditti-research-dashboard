import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import Select from "../fields/select";
import {
  AccessGroup,
  App,
  Permission,
  ResponseBody,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { actionsRaw, resourcesRaw } from "./rolesEdit";
import { SmallLoader } from "../loader";

interface AccessGroupPrefill {
  name: string;
  appSelected: App;
  permissions: Permission[];
}

interface AccessGroupsEditProps extends ViewProps {
  accessGroupId: number;
}

interface AccessGroupsEditState extends AccessGroupPrefill {
  apps: App[];
  loading: boolean;
}

class AccessGroupsEdit extends React.Component<
  AccessGroupsEditProps,
  AccessGroupsEditState
> {
  state = {
    apps: [],
    loading: true,
    name: "",
    appSelected: {} as App,
    permissions: []
  };

  componentDidMount() {
    const apps = makeRequest("/admin/app?app=1").then((apps) =>
      this.setState({ apps })
    );

    const prefill = this.getPrefill().then((prefill) => {
      this.setState({ ...prefill });
    });

    Promise.all([apps, prefill]).then(() => {
      if (!this.state.permissions) this.addPermission();
      this.setState({ loading: false });
    });
  }

  getPrefill = async (): Promise<AccessGroupPrefill> => {
    const id = this.props.accessGroupId;
    return id
      ? makeRequest("/admin/access-group?app=1&id=" + id).then(this.makePrefill)
      : {
          name: "",
          appSelected: {} as App,
          permissions: []
        };
  };

  makePrefill = (res: AccessGroup[]): AccessGroupPrefill => {
    const accessGroup = res[0];
    return {
      name: accessGroup.name,
      appSelected: accessGroup.app,
      permissions: accessGroup.permissions
    };
  };

  selectApp = (id: number): void => {
    const appSelected = this.state.apps.filter((a: App) => a.id == id)[0];
    if (appSelected) this.setState({ appSelected });
  };

  getSelectedApp = (): number => {
    const { appSelected } = this.state;
    return appSelected ? appSelected.id : 0;
  };

  getPermissionFields = (): React.ReactElement => {
    const { permissions } = this.state;

    return (
      <React.Fragment>
        {permissions.map((p: Permission) => {
          return (
            <div key={p.id} className="admin-form-row">
              <div className="admin-form-field border-light">
                <Select
                  id={p.id}
                  opts={actionsRaw.map((a) => {
                    return { value: a.id, label: a.text };
                  })}
                  placeholder="Action"
                  callback={this.selectAction}
                  getDefault={this.getSelectedAction}
                />
              </div>
              <div className="admin-form-field border-light">
                <Select
                  id={p.id}
                  opts={resourcesRaw.map((r) => {
                    return { value: r.id, label: r.text };
                  })}
                  placeholder="Permission"
                  callback={this.selectResource}
                  getDefault={this.getSelectedResource}
                />
              </div>
              <div className="admin-form-field" style={{ flexGrow: 0 }}>
                <button
                  className="button-secondary button-lg"
                  onClick={() => this.removePermission(p.id)}
                >
                  Remove
                </button>
              </div>
            </div>
          );
        })}
      </React.Fragment>
    );
  };

  addPermission = (): void => {
    const permissions: Permission[] = this.state.permissions;
    const id = permissions.length
      ? permissions[permissions.length - 1].id + 1
      : 0;

    permissions.push({ id: id, action: "", resource: "" });
    this.setState({ permissions });
  };

  removePermission = (id: number): void => {
    const permissions = this.state.permissions.filter(
      (p: Permission) => p.id != id
    );

    this.setState({ permissions });
  };

  selectAction = (actionId: number, permissionId: number): void => {
    const action = actionsRaw.filter((a) => a.id == actionId)[0];

    if (action) {
      const { permissions } = this.state;
      const permission: Permission = permissions.filter(
        (p: Permission) => p.id == permissionId
      )[0];

      if (permission) {
        permission.action = action.text;
        this.setState({ permissions });
      }
    }
  };

  getSelectedAction = (id: number): number => {
    const permission: Permission = this.state.permissions.filter(
      (p: Permission) => p.id == id
    )[0];

    if (permission) {
      const actionText = permission.action;
      const action = actionsRaw.filter((a) => a.text == actionText)[0];

      if (action) return action.id;
      else return 0;
    } else {
      return 0;
    }
  };

  selectResource = (resourceId: number, permissionId: number): void => {
    const resource = resourcesRaw.filter((a) => a.id == resourceId)[0];

    if (resource) {
      const { permissions } = this.state;
      const permission: Permission = permissions.filter(
        (p: Permission) => p.id == permissionId
      )[0];

      if (permission) {
        permission.resource = resource.text;
        this.setState({ permissions });
      }
    }
  };

  getSelectedResource = (id: number): number => {
    const permission: Permission = this.state.permissions.filter(
      (p: Permission) => p.id == id
    )[0];

    if (permission) {
      const resourceText = permission.resource;
      const resource = resourcesRaw.filter((a) => a.text == resourceText)[0];

      if (resource) return resource.id;
      else return 0;
    } else {
      return 0;
    }
  };

  post = (): void => {
    const { appSelected, name, permissions } = this.state;
    const ps = permissions.map((p: Permission) => {
      return { action: p.action, resource: p.resource };
    });

    const id = this.props.accessGroupId;
    const data = { app: appSelected.id, name: name, permissions: ps };
    const body = {
      app: 1,
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/access-group/edit" : "/admin/access-group/create";

    makeRequest(url, opts).then(this.handleSuccess).catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    const { goBack, flashMessage } = this.props;

    goBack();
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

  getPermissionsSummary = (): React.ReactElement => {
    return (
      <React.Fragment>
        {this.state.permissions.map((p: Permission) => {
          return p.action || p.resource ? (
            <span key={p.id}>
              &nbsp;&nbsp;&nbsp;&nbsp;
              {p.action + " - " + p.resource}
              <br />
            </span>
          ) : (
            <React.Fragment key={p.id} />
          );
        })}
      </React.Fragment>
    );
  };

  render() {
    const { accessGroupId } = this.props;
    const { name, loading, apps, appSelected } = this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          {loading ? (
            <SmallLoader />
          ) : (
            <div className="admin-form">
              <div className="admin-form-content">
                <h1 className="border-light-b">
                  {accessGroupId ? "Edit " : "Create "} Access Group
                </h1>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="name"
                      type="text"
                      placeholder=""
                      prefill={name}
                      label="Name"
                      onKeyup={(text: string) => this.setState({ name: text })}
                      feedback=""
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <div style={{ marginBottom: "0.5rem" }}>
                      <b>App</b>
                    </div>
                    <div className="border-light">
                      <Select
                        id={accessGroupId}
                        opts={apps.map((a: App) => {
                          return { value: a.id, label: a.name };
                        })}
                        placeholder="Select app..."
                        callback={this.selectApp}
                        getDefault={this.getSelectedApp}
                      />
                    </div>
                  </div>
                </div>
                <div style={{ marginLeft: "2rem", marginBottom: "0.5rem" }}>
                  <b>Add Permissions to Access Group</b>
                </div>
                {this.getPermissionFields()}
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <button
                      className="button-secondary button-lg"
                      onClick={this.addPermission}
                    >
                      Add Permission
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Access Group Summary</h1>
          <span>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br />
            <br />
            App:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{appSelected.name}
            <br />
            <br />
            Permissions:
            <br />
            {this.getPermissionsSummary()}
            <br />
          </span>
          {accessGroupId ? (
            <button className="button-primary" onClick={this.post}>
              Update
            </button>
          ) : (
            <button className="button-primary" onClick={this.post}>
              Create
            </button>
          )}
        </div>
      </div>
    );
  }
}

export default AccessGroupsEdit;
