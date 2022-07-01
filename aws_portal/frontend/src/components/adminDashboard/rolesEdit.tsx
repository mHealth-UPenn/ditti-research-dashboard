import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import Select from "../fields/select";
import { Permission, ResponseBody, Role, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

export const actionsRaw = [
  {
    id: 4,
    text: "View"
  },
  {
    id: 1,
    text: "Create"
  },
  {
    id: 2,
    text: "Edit"
  },
  {
    id: 3,
    text: "Delete"
  },
  {
    id: 5,
    text: "*"
  }
];

export const resourcesRaw = [
  {
    id: 3,
    text: "Accounts"
  },
  {
    id: 1,
    text: "Users"
  },
  {
    id: 2,
    text: "Taps"
  },
  {
    id: 4,
    text: "*"
  },
  {
    id: 5,
    text: "Ditti App Dashboard"
  }
];

interface RolesPrefill {
  name: string;
  permissions: Permission[];
}

interface RolesEditProps extends ViewProps {
  roleId: number;
}

interface RolesEditState extends RolesPrefill {
  loading: boolean;
}

class RolesEdit extends React.Component<RolesEditProps, RolesEditState> {
  state = {
    loading: true,
    name: "",
    permissions: []
  };

  componentDidMount() {
    this.getPrefill().then((prefill: RolesPrefill) =>
      this.setState({ ...prefill }, () => {
        if (!this.state.permissions) this.addPermission();
        this.setState({ loading: false });
      })
    );
  }

  getPrefill = async (): Promise<RolesPrefill> => {
    const id = this.props.roleId;
    return id
      ? makeRequest("/admin/role?app=1&id=" + id).then(this.makePrefill)
      : { name: "", permissions: [] };
  };

  makePrefill = (res: Role[]): RolesPrefill => {
    const role = res[0];

    return {
      name: role.name,
      permissions: role.permissions
    };
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

  post = async (): Promise<void> => {
    const { name, permissions } = this.state;
    const ps = permissions.map((p: Permission) => {
      return { action: p.action, resource: p.resource };
    });

    const data = { name, permissions: ps };
    const id = this.props.roleId;
    const body = {
      app: 1,
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/role/edit" : "/admin/role/create";

    await makeRequest(url, opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
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
    const { roleId } = this.props;
    const { loading, name } = this.state;
    const buttonText = roleId ? "Update" : "Create";

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          {loading ? (
            <SmallLoader />
          ) : (
            <div className="admin-form">
              <div className="admin-form-content">
                <h1 className="border-light-b">
                  {roleId ? "Edit " : "Create "} Role
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
                <div style={{ marginLeft: "2rem", marginBottom: "0.5rem" }}>
                  <b>Add Permissions to Role</b>
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
          <h1 className="border-white-b">Role Summary</h1>
          <span>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br />
            <br />
            Permissions:
            <br />
            {this.getPermissionsSummary()}
          </span>
          <AsyncButton onClick={this.post} text={buttonText} type="primary" />
        </div>
      </div>
    );
  }
}

export default RolesEdit;
