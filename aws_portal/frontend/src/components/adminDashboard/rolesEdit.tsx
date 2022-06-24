import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import Select from "../fields/select";
import { Permission, ResponseBody } from "../../interfaces";
import { makeRequest } from "../../utils";

export const actionsRaw = [
  {
    id: 4,
    text: "View"
  },
  {
    id: 1,
    text: "Add"
  },
  {
    id: 2,
    text: "Edit"
  },
  {
    id: 3,
    text: "Delete"
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
  }
];

interface RolesEditProps {
  roleId: number;
}

interface RolesEditState {
  name: string;
  permissions: Permission[];
}

class RolesEdit extends React.Component<RolesEditProps, RolesEditState> {
  constructor(props: RolesEditProps) {
    super(props);
    const { roleId } = props;
    const prefill = roleId
      ? this.getPrefill(roleId)
      : {
          name: "",
          permissions: []
        };

    this.state = {
      name: prefill.name,
      permissions: prefill.permissions
    };
  }

  componentDidMount() {
    if (!this.state.permissions) this.addPermission();
  }

  getPrefill(id: number) {
    return {
      name: "",
      permissions: []
    };
  }

  getPermissionFields = (): React.ReactElement => {
    const { permissions } = this.state;

    return (
      <React.Fragment>
        {permissions.map((p) => {
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
    const { permissions } = this.state;
    const id = permissions.length
      ? permissions[permissions.length - 1].id + 1
      : 0;
    permissions.push({ id: id, action: "", resource: "" });
    this.setState({ permissions });
  };

  removePermission = (id: number): void => {
    const permissions = this.state.permissions.filter((p) => p.id != id);
    this.setState({ permissions });
  };

  selectAction = (actionId: number, permissionId: number): void => {
    const action = actionsRaw.filter((a) => a.id == actionId)[0];

    if (action) {
      const { permissions } = this.state;
      const permission = permissions.filter((p) => p.id == permissionId)[0];

      if (permission) {
        permission.action = action.text;
        this.setState({ permissions });
      }
    }
  };

  getSelectedAction = (id: number): number => {
    const permission = this.state.permissions.filter((p) => p.id == id)[0];

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
      const permission = permissions.filter((p) => p.id == permissionId)[0];

      if (permission) {
        permission.resource = resource.text;
        this.setState({ permissions });
      }
    }
  };

  getSelectedResource = (id: number): number => {
    const permission = this.state.permissions.filter((p) => p.id == id)[0];

    if (permission) {
      const resourceText = permission.resource;
      const resource = resourcesRaw.filter((a) => a.text == resourceText)[0];
      if (resource) return resource.id;
      else return 0;
    } else {
      return 0;
    }
  };

  create = (): void => {
    const { name, permissions } = this.state;
    const ps = permissions.map((p) => {
      return { action: p.action, resource: p.resource };
    });

    const body = {
      app: 1,
      create: {
        name: name,
        permissions: ps
      }
    };

    const opts = {
      method: "POST",
      body: JSON.stringify(body)
    };

    makeRequest("/admin/role/create", opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    console.log(res.msg);
  };

  handleFailure = (res: ResponseBody) => {
    console.log(res.msg);
  };

  getPermissionsSummary = (): React.ReactElement => {
    return (
      <React.Fragment>
        {this.state.permissions.map((p) => {
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
    const { name } = this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {roleId ? "Edit " : "Create "} Role
              </h1>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="name"
                    svg={<React.Fragment />}
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
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Role Summary</h1>
          <span>
            Name: {name}
            <br />
            <br />
            Permissions:
            <br />
            {this.getPermissionsSummary()}
          </span>
          <button className="button-primary" onClick={this.create}>
            Create
          </button>
        </div>
      </div>
    );
  }
}

export default RolesEdit;
