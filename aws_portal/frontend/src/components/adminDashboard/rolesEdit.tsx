import React, { useState, useEffect } from "react";
import TextField from "../fields/textField";
import Select from "../fields/select";
import {
  ActionResource,
  Permission,
  ResponseBody,
  Role,
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import FormView from "../containers/forms/formView";
import Form from "../containers/forms/form";
import FormSummary from "../containers/forms/formSummary";
import FormTitle from "../text/formTitle";
import FormRow from "../containers/forms/formRow";
import FormField from "../containers/forms/formField";
import Button from "../buttons/button";
import FormSummaryTitle from "../text/formSummaryTitle";
import FormSummaryText from "../containers/forms/formSummaryText";
import FormSummaryButton from "../containers/forms/formSummaryButton";
import CloseIcon from "@mui/icons-material/Close";
import FormSummaryContent from "../containers/forms/formSummaryContent";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";

/**
 * The form's prefill
 */
interface RolesPrefill {
  name: string;
  permissions: Permission[];
}

const RolesEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const roleId = id ? parseInt(id) : 0

  const [actions, setActions] = useState<ActionResource[]>([]);
  const [resources, setResources] = useState<ActionResource[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [name, setName] = useState<string>("");
  const [permissions, setPermissions] = useState<Permission[]>([]);

  const { flashMessage } = useFlashMessageContext();
  const navigate = useNavigate();

  useEffect(() => {

    // get all available actions
    const fetchActions = makeRequest("/admin/action?app=1").then(
      (actions: ActionResource[]) => setActions(actions)
    );

    // get all available resources
    const fetchResources = makeRequest("/admin/resource?app=1").then(
      (resources: ActionResource[]) => setResources(resources)
    );

    // set any form prefill data
    const prefill = getPrefill().then((prefill: RolesPrefill) => {
      setName(prefill.name);
      setPermissions(prefill.permissions);
    });

    // when all promises are complete, hide the loader
    Promise.all([fetchActions, fetchResources, prefill]).then(() => {
      setLoading(false);
    });
  }, []);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<RolesPrefill> => {
    const id = roleId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/role?app=1&id=" + id).then(makePrefill)
      : { name: "", permissions: [] };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (res: Role[]): RolesPrefill => {
    const role = res[0];

    return {
      name: role.name,
      permissions: role.permissions
    };
  };

  /**
   * Add a new permission and pair of action and resource dropdown menus
   */
  const addPermission = (): void => {
    const id = permissions.length ? permissions[permissions.length - 1].id + 1 : 0;
    setPermissions([...permissions, { id: id, action: "", resource: "" }]);
  };

  /**
   * Remove a permission and pair of action and resource dropdown menus
   * @param id - the database primary key
   */
  const removePermission = (id: number): void => {
    setPermissions(permissions.filter((p: Permission) => p.id !== id));
  };

  /**
   * Select a new action for a given permission
   * @param actionId - the action's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectAction = (actionId: number, permissionId: number): void => {
    const action = actions.find((a: ActionResource) => a.id === actionId);

    if (action) {
      setPermissions(
        permissions.map((p: Permission) =>
          p.id === permissionId ? { ...p, action: action.value } : p
        )
      );
    }
  };

  /**
   * Get the selected action for a given permission
   * @param id - the permission's database primary key
   * @returns - the action's database primary key
   */
  const getSelectedAction = (id: number): number => {
    const permission = permissions.find((p: Permission) => p.id === id);
    const action = actions.find((a: ActionResource) => a.value === permission?.action);
    return action ? action.id : 0;
  };

  /**
   * Select a new resource for a given permission
   * @param resourceId - the resource's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectResource = (resourceId: number, permissionId: number): void => {
    const resource = resources.find((r: ActionResource) => r.id === resourceId);

    if (resource) {
      setPermissions(
        permissions.map((p: Permission) =>
          p.id === permissionId ? { ...p, resource: resource.value } : p
        )
      );
    }
  };

  /**
   * Get the currently selected resource for a given permission
   * @param id - the permission's database primary key
   * @returns - the permission's database primary key
   */
  const getSelectedResource = (id: number): number => {
    const permission = permissions.find((p: Permission) => p.id === id);
    const resource = resources.find((r: ActionResource) => r.value === permission?.resource);
    return resource ? resource.id : 0;
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async (): Promise<void> => {
    const ps = permissions.map((p: Permission) => ({
      action: p.action,
      resource: p.resource
    }));

    const data = { name, permissions: ps };
    const id = roleId;
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/role/edit" : "/admin/role/create";

    await makeRequest(url, opts)
      .then(handleSuccess)
      .catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // go back to the list view and flash a message
    navigate(-1);
    flashMessage(<span>{res.msg}</span>, "success");
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message from the backend or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
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
  const getPermissionsSummary = (): React.ReactElement => {
    return (
      <React.Fragment>
        {permissions.map((p: Permission) => {

          // handle wildcard permissions
          const action = p.action === "*" ? "All Actions" : p.action;
          const resource = p.resource === "*" ? "All Resources" : p.resource;

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

  const permissionFields = permissions.map((p: Permission, i) =>
    <FormRow key={i} forceRow={true}>
      <FormField className="mr-4 xl:mr-8">
        <Select
          id={p.id}
          opts={actions.map((a: ActionResource) => ({
            value: a.id,
            label: a.value
          }))}
          placeholder="Action"
          callback={selectAction}
          getDefault={getSelectedAction} />
      </FormField>
      <FormField>
        <Select
          id={p.id}
          opts={resources.map((r: ActionResource) => ({
            value: r.id,
            label: r.value
          }))}
          placeholder="Permission"
          callback={selectResource}
          getDefault={getSelectedResource} />
      </FormField>
      <div className="flex items-center mb-8 px-2 cursor-pointer lg:pr-4">
        <CloseIcon
          color="warning"
          fontSize="large"
          onClick={() => removePermission(p.id)} />
      </div>
    </FormRow>
  );

  const buttonText = roleId ? "Update" : "Create";

  if (loading) {
    return (
      <FormView>
        <Form>
          <SmallLoader />
        </Form>
      </FormView>
    );
  }

  return (
    <FormView>
      <Form>
        <FormTitle>{roleId ? "Edit " : "Create "} Role</FormTitle>
        <FormRow>
          <FormField>
            <TextField
              id="name"
              type="text"
              placeholder=""
              value={name}
              label="Name"
              onKeyup={(text: string) => setName(text)}
              feedback="" />
          </FormField>
        </FormRow>
        <FormRow>
          <span className="mb-1 px-4">Add Permissions to Role</span>
        </FormRow>
        {permissionFields}
        <FormRow>
          <FormField>
            <Button
              variant="tertiary"
              onClick={addPermission}
              className="w-max"
              size="sm">
                Add Permission
            </Button>
          </FormField>
        </FormRow>
      </Form>
      <FormSummary>
        <FormSummaryTitle>Role Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br />
            <br />
            Permissions:
            <br />
            {getPermissionsSummary()}
          </FormSummaryText>
          <FormSummaryButton onClick={post}>
            {buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};

export default RolesEdit;
