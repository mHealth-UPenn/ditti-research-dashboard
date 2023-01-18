import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import Select from "../fields/select";
import {
  ActionResource,
  Permission,
  ResponseBody,
  Role,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

/**
 * The form's prefill
 */
interface RolesPrefill {
  name: string;
  permissions: Permission[];
}

/**
 * roleId: the database primary key, 0 if creating a new entry
 */
interface RolesEditProps extends ViewProps {
  roleId: number;
}

/**
 * actions: all available actions for selection
 * resources: all available resources for selection
 * loading: whether to show the loader
 */
interface RolesEditState extends RolesPrefill {
  actions: ActionResource[];
  resources: ActionResource[];
  loading: boolean;
}

class RolesEdit extends React.Component<RolesEditProps, RolesEditState> {
  state = {
    actions: [],
    resources: [],
    loading: true,
    name: "",
    permissions: []
  };

  componentDidMount() {

    // get all available actions
    const actions = makeRequest("/admin/action?app=1").then(
      (actions: ActionResource[]) => this.setState({ actions })
    );

    // get all available resources
    const resources = makeRequest("/admin/resource?app=1").then(
      (resources: ActionResource[]) => this.setState({ resources })
    );

    // set any form prefill data
    const prefill = this.getPrefill().then((prefill: RolesPrefill) =>
      this.setState({ ...prefill })
    );

    // when all promises are complete, hide the loader
    Promise.all([actions, resources, prefill]).then(() => {
      if (!this.state.permissions) this.addPermission();
      this.setState({ loading: false });
    });
  }

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  getPrefill = async (): Promise<RolesPrefill> => {
    const id = this.props.roleId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/role?app=1&id=" + id).then(this.makePrefill)
      : { name: "", permissions: [] };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  makePrefill = (res: Role[]): RolesPrefill => {
    const role = res[0];

    return {
      name: role.name,
      permissions: role.permissions
    };
  };

  /**
   * Get the action and resource dropdown menus for each permission
   * @returns - the permission fields
   */
  getPermissionFields = (): React.ReactElement => {
    const { actions, resources, permissions } = this.state;

    return (
      <React.Fragment>
        {permissions.map((p: Permission) => {
          return (
            <div key={p.id} className="admin-form-row">
              <div className="admin-form-field border-light">
                <Select
                  id={p.id}
                  opts={actions.map((a: ActionResource) => {
                    return { value: a.id, label: a.value };
                  })}
                  placeholder="Action"
                  callback={this.selectAction}
                  getDefault={this.getSelectedAction}
                />
              </div>
              <div className="admin-form-field border-light">
                <Select
                  id={p.id}
                  opts={resources.map((r: ActionResource) => {
                    return { value: r.id, label: r.value };
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

  /**
   * Add a new permission and pair of action and resource dropdown menus
   */
  addPermission = (): void => {
    const permissions: Permission[] = this.state.permissions;

    // set the key to 0 or the last field's id + 1
    const id = permissions.length
      ? permissions[permissions.length - 1].id + 1
      : 0;

    // add the permission field to the page
    permissions.push({ id: id, action: "", resource: "" });
    this.setState({ permissions });
  };

  /**
   * Remove a permission and pair of action and resource dropdown menus
   * @param id - the database primary key
   */
  removePermission = (id: number): void => {
    const permissions = this.state.permissions.filter(
      (p: Permission) => p.id != id
    );

    this.setState({ permissions });
  };

  /**
   * Select a new action for a given permission
   * @param actionId - the action's database primary key
   * @param permissionId - the permission's database primary key
   */
  selectAction = (actionId: number, permissionId: number): void => {

    // get the new action
    const action: ActionResource = this.state.actions.filter(
      (a: ActionResource) => a.id == actionId
    )[0];

    if (action) {
      const { permissions } = this.state;

      // get the permission
      const permission: Permission = permissions.filter(
        (p: Permission) => p.id == permissionId
      )[0];

      if (permission) {

        // set the new action
        permission.action = action.value;
        this.setState({ permissions });
      }
    }
  };

  /**
   * Get the selected action for a given permission
   * @param id - the permission's database primary key
   * @returns - the action's database primary key
   */
  getSelectedAction = (id: number): number => {

    // get the permission
    const permission: Permission = this.state.permissions.filter(
      (p: Permission) => p.id == id
    )[0];

    if (permission) {
      const actionText = permission.action;

      // get the action
      const action: ActionResource = this.state.actions.filter(
        (a: ActionResource) => a.value == actionText
      )[0];

      if (action) return action.id;
      else return 0;
    } else {
      return 0;
    }
  };

  /**
   * Select a new resource for a given permission
   * @param resourceId - the resource's database primary key
   * @param permissionId - the permission's database primary key
   */
  selectResource = (resourceId: number, permissionId: number): void => {

    // get the new resource
    const resource: ActionResource = this.state.resources.filter(
      (r: ActionResource) => r.id == resourceId
    )[0];

    if (resource) {
      const { permissions } = this.state;

      // get the permission
      const permission: Permission = permissions.filter(
        (p: Permission) => p.id == permissionId
      )[0];

      if (permission) {

        // set the new resource
        permission.resource = resource.value;
        this.setState({ permissions });
      }
    }
  };

  /**
   * Get the currently selected resource for a given permission
   * @param id - the permission's database primary key
   * @returns - the permission's database primary key
   */
  getSelectedResource = (id: number): number => {

    // get the permission
    const permission: Permission = this.state.permissions.filter(
      (p: Permission) => p.id == id
    )[0];

    if (permission) {
      const resourceText = permission.resource;

      // get the resource
      const resource: ActionResource = this.state.resources.filter(
        (r: ActionResource) => r.value == resourceText
      )[0];

      if (resource) return resource.id;
      else return 0;
    } else {
      return 0;
    }
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  post = async (): Promise<void> => {
    const { name, permissions } = this.state;
    const ps = permissions.map((p: Permission) => {
      return { action: p.action, resource: p.resource };
    });

    const data = { name, permissions: ps };
    const id = this.props.roleId;
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/role/edit" : "/admin/role/create";

    await makeRequest(url, opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  handleSuccess = (res: ResponseBody) => {
    const { goBack, flashMessage } = this.props;

    // go back to the list view and flash a message
    goBack();
    flashMessage(<span>{res.msg}</span>, "success");
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    // flash the message from the backend or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  /**
   * Compile the role's permissions as HTML for the entry summary
   * @returns - the permissions summary
   */
  getPermissionsSummary = (): React.ReactElement => {
    return (
      <React.Fragment>
        {this.state.permissions.map((p: Permission) => {

          // handle wildcard permissions
          const action = p.action == "*" ? "All Actions" : p.action;
          const resource = p.resource == "*" ? "All Resources" : p.resource;

          // don't compile empty permissions that have no action or resource selected
          return action || resource ? (
            <span key={p.id}>
              &nbsp;&nbsp;&nbsp;&nbsp;
              {action + " - " + resource}
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

        {/* the edit/create form */}
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

          {/* the edit/create summary */}
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
