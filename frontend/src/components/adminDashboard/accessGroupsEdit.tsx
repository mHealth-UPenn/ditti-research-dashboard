/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { TextField } from "../fields/textField";
import { SelectField } from "../fields/selectField";
import { AccessGroup, ActionResource, App, Permission } from "../../types/api";
import { httpClient } from "../../lib/http";
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
import { AccessGroupFormPrefill } from "./adminDashboard.types";
import { useApiHandler } from "../../hooks/useApiHandler";

export const AccessGroupsEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const accessGroupId = id ? parseInt(id) : 0;

  const [actions, setActions] = useState<ActionResource[]>([]);
  const [resources, setResources] = useState<ActionResource[]>([]);
  const [apps, setApps] = useState<App[]>([]);
  const [name, setName] = useState<string>("");
  const [appSelected, setAppSelected] = useState<App>({} as App);
  const [permissions, setPermissions] = useState<Permission[]>([]);

  const navigate = useNavigate();

  // Hook for handling API requests with loading state and notifications
  const { safeRequest: safeFetchData, isLoading: isLoadingData } =
    useApiHandler<{
      actions: ActionResource[];
      resources: ActionResource[];
      apps: App[];
      prefill: AccessGroupFormPrefill;
    }>({
      errorMessage: "Failed to load access group data.",
      showDefaultSuccessMessage: false,
    });

  // Hook for handling the form submission
  const { safeRequest: safeSubmit, isLoading: isSubmitting } = useApiHandler<{
    msg?: string;
  }>({
    successMessage: (data) => data.msg ?? "Access group saved successfully.",
    errorMessage: (error) => `Failed to save access group: ${error.message}`,
    onSuccess: () => {
      // Go back to the list view after successful save
      navigate(-1);
    },
  });

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (res: AccessGroup[]): AccessGroupFormPrefill => {
    const accessGroup = res[0];
    return {
      name: accessGroup.name,
      appSelected: accessGroup.app,
      permissions: accessGroup.permissions,
    };
  };

  // Define addPermission - useCallback might be needed if exhaustive-deps complains
  const addPermission = useCallback((): void => {
    setPermissions((prevPermissions) => {
      const id = prevPermissions.length
        ? prevPermissions[prevPermissions.length - 1].id + 1
        : 0;
      return [...prevPermissions, { id: id, action: "", resource: "" }];
    });
  }, []);

  useEffect(() => {
    /** Fetches initial data (actions, resources, apps, prefill) */
    const fetchData = async () => {
      const fetchedData = await safeFetchData(async () => {
        const id = accessGroupId;

        // Define requests
        const actionsReq = httpClient.request<ActionResource[]>(
          "/admin/action?app=1"
        );
        const resourcesReq = httpClient.request<ActionResource[]>(
          "/admin/resource?app=1"
        );
        const appsReq = httpClient.request<App[]>("/admin/app?app=1");
        const prefillReq = id
          ? httpClient.request<AccessGroup[]>(
              `/admin/access-group?app=1&id=${String(id)}`
            )
          : Promise.resolve(null); // Resolve with null if creating new

        // Execute requests in parallel
        const [
          actionsResponse,
          resourcesResponse,
          appsResponse,
          prefillResponse,
        ] = await Promise.all([actionsReq, resourcesReq, appsReq, prefillReq]);

        // Process prefill data
        const prefillData = prefillResponse
          ? makePrefill(prefillResponse)
          : { name: "", appSelected: {} as App, permissions: [] };

        return {
          actions: actionsResponse,
          resources: resourcesResponse,
          apps: appsResponse,
          prefill: prefillData,
        };
      });

      // Update state if data fetching was successful
      if (fetchedData) {
        setActions(fetchedData.actions);
        setResources(fetchedData.resources);
        setApps(fetchedData.apps);
        const prefillData = fetchedData.prefill;
        setName(prefillData.name);
        setAppSelected(prefillData.appSelected);
        setPermissions(prefillData.permissions);

        if (!accessGroupId && !prefillData.permissions.length) addPermission();
      } else {
        // Handle fetch error (message shown by hook)
        if (accessGroupId) {
          // If editing failed to load, navigate back
          navigate(-1);
        }
      }
    };

    void fetchData();
  }, [accessGroupId, addPermission, safeFetchData, navigate]);

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
  const getSelectedApp = (): number => appSelected.id || 0;

  /**
   * Remove a permission and pair of action and resource dropdown menus
   * @param id - the database primary key
   */
  const removePermission = (id: number): void => {
    setPermissions((prevPermissions) =>
      prevPermissions.filter((p) => p.id !== id)
    );
  };

  /**
   * Select a new action for a given permission
   * @param actionId - the action's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectAction = (actionId: number, permissionId: number): void => {
    const action = actions.find((a) => a.id === actionId);
    if (action) {
      setPermissions((prevPermissions) =>
        prevPermissions.map((p) =>
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
    const permission = permissions.find((p) => p.id === id);
    if (permission) {
      const action = actions.find((a) => a.value === permission.action);
      return action ? action.id : 0;
    }
    return 0;
  };

  /**
   * Select a new resource for a given permission
   * @param resourceId - the resource's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectResource = (resourceId: number, permissionId: number): void => {
    const resource = resources.find((r) => r.id === resourceId);
    if (resource) {
      setPermissions((prevPermissions) =>
        prevPermissions.map((p) =>
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
    const permission = permissions.find((p) => p.id === id);
    if (permission) {
      const resource = resources.find((r) => r.value === permission.resource);
      return resource ? resource.id : 0;
    }
    return 0;
  };

  /**
   * Get the action and resource dropdown menus for each permission
   * @returns - the permission fields
   */
  const permissionFields = permissions.map((p: Permission) => (
    <FormRow key={p.id} forceRow={true}>
      <FormField className="mr-4 xl:mr-8">
        <SelectField
          id={p.id}
          disabled={isLoadingData || isSubmitting}
          opts={actions.map((a) => ({ value: a.id, label: a.value }))}
          placeholder="Action"
          callback={selectAction}
          getDefault={() => getSelectedAction(p.id)}
        />
      </FormField>
      <FormField>
        <SelectField
          id={p.id}
          disabled={isLoadingData || isSubmitting}
          opts={resources.map((r) => ({ value: r.id, label: r.value }))}
          placeholder="Permission"
          callback={selectResource}
          getDefault={() => getSelectedResource(p.id)}
        />
      </FormField>
      <div className="mb-8 flex cursor-pointer items-center px-2 lg:pr-4">
        <CloseIcon
          color="warning"
          fontSize="large"
          onClick={() => {
            if (!isLoadingData && !isSubmitting) {
              removePermission(p.id);
            }
          }}
        />
      </div>
    </FormRow>
  ));

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async (): Promise<void> => {
    const ps = permissions.map((p) => ({
      action: p.action,
      resource: p.resource,
    }));

    const id = accessGroupId;
    const payload = { app: appSelected.id, name: name, permissions: ps };
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: payload } : { create: payload }),
    };

    const url = id ? "/admin/access-group/edit" : "/admin/access-group/create";

    // Use safeSubmit from useApiHandler
    await safeSubmit(async () => {
      // Define the expected response type for the request
      const response = await httpClient.request<{ msg?: string }>(url, {
        method: "POST",
        data: body,
      });
      return response; // Return the data for the hook's onSuccess handler
    });
  };

  /**
   * Compile the access group's permissions as HTML for the entry summary
   * @returns - the permissions summary
   */
  const getPermissionsSummary = useMemo((): React.ReactElement => {
    // Filter out permissions that haven't been fully selected yet before mapping
    const validPermissions = permissions.filter((p) => p.action && p.resource);

    if (validPermissions.length === 0) {
      return <i>No permissions added yet.</i>;
    }

    return (
      <>
        {validPermissions.map((p: Permission) => {
          // handle wildcard permissions
          const action = p.action === "*" ? "All Actions" : p.action;
          const resource = p.resource === "*" ? "All Resources" : p.resource;

          // Now we know action and resource are non-empty
          return (
            <span key={p.id}>
              &nbsp;&nbsp;&nbsp;&nbsp;
              {action + " - " + resource}
              <br />
            </span>
          );
        })}
      </>
    );
  }, [permissions]);

  const buttonText = accessGroupId ? "Update" : "Create";
  const isProcessing = isLoadingData || isSubmitting; // Combine loading states

  if (isLoadingData) {
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
        <FormTitle>
          {accessGroupId ? "Edit " : "Create "} Access Group
        </FormTitle>
        <FormRow>
          <FormField>
            <TextField
              disabled={isProcessing}
              id="name"
              type="text"
              placeholder=""
              value={name}
              label="Name"
              onKeyup={(text: string) => {
                setName(text);
              }}
              feedback=""
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <div className="mb-1">App</div>
            <div className="border-light">
              <SelectField
                disabled={isProcessing}
                id={accessGroupId || 0}
                opts={apps.map((a: App) => ({
                  value: a.id,
                  label: a.name,
                }))}
                placeholder="Select app..."
                callback={selectApp}
                getDefault={getSelectedApp}
              />
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
              disabled={isProcessing}
              variant="tertiary"
              onClick={addPermission}
              className="w-max"
              size="sm"
            >
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
          <FormSummaryButton onClick={post} disabled={isProcessing}>
            {isSubmitting ? "Saving..." : buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
