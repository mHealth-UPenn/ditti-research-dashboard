/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { TextField } from "../fields/textField";
import { SelectField } from "../fields/selectField";
import {
  AccessGroup,
  ActionResource,
  App,
  Permission,
  ResponseBody,
} from "../../types/api";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { Button } from "../buttons/button";
import { FormSummary } from "../containers/forms/formSummary";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import CloseIcon from "@mui/icons-material/Close";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";

/**
 * The form's prefill
 */
interface AccessGroupPrefill {
  name: string;
  appSelected: App;
  permissions: Permission[];
}


export const AccessGroupsEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const accessGroupId = id ? parseInt(id) : 0

  const [actions, setActions] = useState<ActionResource[]>([]);
  const [resources, setResources] = useState<ActionResource[]>([]);
  const [apps, setApps] = useState<App[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [name, setName] = useState<string>("");
  const [appSelected, setAppSelected] = useState<App>({} as App);
  const [permissions, setPermissions] = useState<Permission[]>([]);

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch all available actions
        const actions = await makeRequest("/admin/action?app=1");
        setActions(actions);

        // Fetch all available resources
        const resources = await makeRequest("/admin/resource?app=1");
        setResources(resources);

        // Fetch all available apps
        const apps = await makeRequest("/admin/app?app=1");
        setApps(apps);

        // Fetch any form prefill data
        const prefillData = await getPrefill();
        setName(prefillData.name);
        setAppSelected(prefillData.appSelected);
        setPermissions(prefillData.permissions);

        if (!prefillData.permissions.length) addPermission();
      } finally {
        // Hide the loader after all requests
        setLoading(false);
      }
    };

    fetchData();
  }, [accessGroupId]);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<AccessGroupPrefill> => {
    const id = accessGroupId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/access-group?app=1&id=" + id).then(makePrefill)
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
  const makePrefill = (res: AccessGroup[]): AccessGroupPrefill => {
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
  const selectApp = (id: number): void => {
    const appSelected = apps.find((a) => a.id === id);
    if (appSelected) setAppSelected(appSelected);
  };

  /**
   * Get the currently selected app
   * @returns - the database primary key
   */
  const getSelectedApp = (): number => (appSelected ? appSelected.id : 0);

  /**
   * Add a new permission and pair of action and resource dropdown menus
   */
  const addPermission = useCallback((): void => {
    setPermissions((prevPermissions) => {
      const id = prevPermissions.length ? prevPermissions[prevPermissions.length - 1].id + 1 : 0;
      return [...prevPermissions, { id: id, action: "", resource: "" }];
    });
  }, []);

  /**
   * Remove a permission and pair of action and resource dropdown menus
   * @param id - the database primary key
   */
  const removePermission = useCallback((id: number): void => {
    setPermissions((prevPermissions) =>
      prevPermissions.filter((p) => p.id !== id)
    );
  }, []);

  /**
   * Select a new action for a given permission
   * @param actionId - the action's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectAction = useCallback((actionId: number, permissionId: number): void => {
    const action = actions.find((a) => a.id === actionId);
    if (action) {
      setPermissions((prevPermissions) =>
        prevPermissions.map((p) =>
          p.id === permissionId ? { ...p, action: action.value } : p
        )
      );
    }
  }, [actions]);

  /**
   * Get the selected action for a given permission
   * @param id - the permission's database primary key
   * @returns - the action's database primary key
   */
  const getSelectedAction = useCallback((id: number): number => {
    const permission = permissions.find((p) => p.id === id);
    if (permission) {
      const action = actions.find((a) => a.value === permission.action);
      return action ? action.id : 0;
    }
    return 0;
  }, [permissions, actions]);

  /**
   * Select a new resource for a given permission
   * @param resourceId - the resource's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectResource = useCallback((resourceId: number, permissionId: number): void => {
    const resource = resources.find((r) => r.id === resourceId);
    if (resource) {
      setPermissions((prevPermissions) =>
        prevPermissions.map((p) =>
          p.id === permissionId ? { ...p, resource: resource.value } : p
        )
      );
    }
  }, [resources]);

  /**
   * Get the currently selected resource for a given permission
   * @param id - the permission's database primary key
   * @returns - the permission's database primary key
   */
  const getSelectedResource = useCallback((id: number): number => {
    const permission = permissions.find((p) => p.id === id);
    if (permission) {
      const resource = resources.find((r) => r.value === permission.resource);
      return resource ? resource.id : 0;
    }
    return 0;
  }, [permissions, resources]);

  /**
   * Get the action and resource dropdown menus for each permission
   * @returns - the permission fields
   */
  const permissionFields =permissions.map((p: Permission) =>
    <FormRow key={p.id} forceRow={true}>
      <FormField className="mr-4 xl:mr-8">
        <SelectField
          id={p.id}
          opts={actions.map((a) => ({ value: a.id, label: a.value }))}
          placeholder="Action"
          callback={selectAction}
          getDefault={() => getSelectedAction(p.id)} />
      </FormField>
      <FormField>
        <SelectField
          id={p.id}
          opts={resources.map((r) => ({ value: r.id, label: r.value }))}
          placeholder="Permission"
          callback={selectResource}
          getDefault={() => getSelectedResource(p.id)} />
      </FormField>
      <div className="flex items-center mb-8 px-2 cursor-pointer lg:pr-4">
        <CloseIcon
          color="warning"
          fontSize="large"
          onClick={() => removePermission(p.id)} />
      </div>
    </FormRow>
  );

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async (): Promise<void> => {
    const ps = permissions.map((p) => ({
      action: p.action,
      resource: p.resource
    }));

    const id = accessGroupId;
    const data = { app: appSelected.id, name: name, permissions: ps };
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/access-group/edit" : "/admin/access-group/create";

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
   * Compile the access group's permissions as HTML for the entry summary
   * @returns - the permissions summary
   */
  const getPermissionsSummary = useMemo((): React.ReactElement => {
    return (
      <>
        {permissions.map((p: Permission) => {
          // handle wildcard permissions
          const action = p.action === "*" ? "All Actions" : p.action;
          const resource = p.resource === "*" ? "All Resources" : p.resource;

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
      </>
    );
  }, [permissions]);

  const buttonText = accessGroupId ? "Update" : "Create";

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
        <FormTitle>{accessGroupId ? "Edit " : "Create "} Access Group</FormTitle>
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
          <FormField>
            <div className="mb-1">App</div>
            <div className="border-light">
              <SelectField
                id={accessGroupId || 0}
                opts={apps.map((a: App) => ({
                  value: a.id,
                  label: a.name
                }))}
                placeholder="Select app..."
                callback={selectApp}
                getDefault={getSelectedApp} />
            </div>
          </FormField>
        </FormRow>
        <FormRow>
          <span className="mb-1 px-4">Add Permissions to Access Group</span>
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
        <FormSummaryTitle>Access Group Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
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
            {getPermissionsSummary}
            <br />
          </FormSummaryText>
          <FormSummaryButton onClick={post}>
            {buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
