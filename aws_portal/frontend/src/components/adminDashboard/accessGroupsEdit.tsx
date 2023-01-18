import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import Select from "../fields/select";
import {
  AccessGroup,
  ActionResource,
  App,
  Permission,
  ResponseBody,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

/**
 * The form's prefill
 */
interface AccessGroupPrefill {
  name: string;
  appSelected: App;
  permissions: Permission[];
}

/**
 * accessGroupId: the database primary key, 0 if creating a new entry
 */
interface AccessGroupsEditProps extends ViewProps {
  accessGroupId: number;
}

/**
 * actions: all available actions for selection
 * resources: all available resources for selection
 * apps: all available apps for selection
 * loading: whether to show the loader
 */
interface AccessGroupsEditState extends AccessGroupPrefill {
  actions: ActionResource[];
  resources: ActionResource[];
  apps: App[];
  loading: boolean;
}

class AccessGroupsEdit extends React.Component<
  AccessGroupsEditProps,
  AccessGroupsEditState
> {
  state = {
    actions: [],
    resources: [],
    apps: [],
    loading: true,
    name: "",
    appSelected: {} as App,
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

    // get all available apps
    const apps = makeRequest("/admin/app?app=1").then((apps) =>
      this.setState({ apps })
    );

    // set any form prefill data
    const prefill = this.getPrefill().then((prefill) => {
      this.setState({ ...prefill });
    });

    // when all promises are complete, hide the loader
    Promise.all([actions, resources, apps, prefill]).then(() => {
      if (!this.state.permissions) this.addPermission();
      this.setState({ loading: false });
    });
  }

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  getPrefill = async (): Promise<AccessGroupPrefill> => {
    const id = this.props.accessGroupId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/access-group?app=1&id=" + id).then(this.makePrefill)
      : {
          name: "",
          appSelected: {} as App,
          permissions: []
        };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  makePrefill = (res: AccessGroup[]): AccessGroupPrefill => {
    const accessGroup = res[0];
    return {
      name: accessGroup.name,
      appSelected: accessGroup.app,
      permissions: accessGroup.permissions
    };
  };

  /**
   * Change the selected app when one is chosen from the dropdown menu
   * @param id - the database primary key
   */
  selectApp = (id: number): void => {
    const appSelected = this.state.apps.filter((a: App) => a.id == id)[0];
    if (appSelected) this.setState({ appSelected });
  };

  /**
   * Get the currently selected app
   * @returns - the database primary key
   */
  getSelectedApp = (): number => {
    const { appSelected } = this.state;
    return appSelected ? appSelected.id : 0;
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
    const { appSelected, name, permissions } = this.state;
    const ps = permissions.map((p: Permission) => {
      return { action: p.action, resource: p.resource };
    });

    const id = this.props.accessGroupId;
    const data = { app: appSelected.id, name: name, permissions: ps };
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/access-group/edit" : "/admin/access-group/create";

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
   * Compile the access group's permissions as HTML for the entry summary
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
          return p.action || p.resource ? (
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
    const { accessGroupId } = this.props;
    const { name, loading, apps, appSelected } = this.state;
    const buttonText = accessGroupId ? "Update" : "Create";

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

        {/* the edit/create summary */}
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
          <AsyncButton onClick={this.post} text={buttonText} type="primary" />
        </div>
      </div>
    );
  }
}

export default AccessGroupsEdit;
