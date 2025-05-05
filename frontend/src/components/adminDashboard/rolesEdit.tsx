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

import React, { useState, useEffect, useCallback } from "react";
import { TextField } from "../fields/textField";
import { SelectField } from "../fields/selectField";
import {
  ActionResource,
  Permission,
  ResponseBody,
  Role,
} from "../../types/api";
import { httpClient } from "../../lib/http";
import { SmallLoader } from "../loader/loader";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormSummary } from "../containers/forms/formSummary";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { Button } from "../buttons/button";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import CloseIcon from "@mui/icons-material/Close";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { RolesFormPrefill } from "./adminDashboard.types";
import { useApiHandler } from "../../hooks/useApiHandler";

export const RolesEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const roleId = id ? parseInt(id) : 0;

  const [actions, setActions] = useState<ActionResource[]>([]);
  const [resources, setResources] = useState<ActionResource[]>([]);
  const [name, setName] = useState<string>("");
  const [permissions, setPermissions] = useState<Permission[]>([]);

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  const { safeRequest: safeFetchInitialData, isLoading: isLoadingData } =
    useApiHandler<{
      actions: ActionResource[];
      resources: ActionResource[];
      prefill: RolesFormPrefill;
    }>({
      errorMessage: "Failed to load role edit data.",
      showDefaultSuccessMessage: false,
    });

  const { safeRequest: safeSubmit, isLoading: isSubmitting } =
    useApiHandler<ResponseBody>({
      successMessage: (data) => data.msg,
      errorMessage: (error) => `Failed to save role: ${error.message}`,
      onSuccess: () => {
        navigate(-1);
      },
    });

  const addPermission = useCallback((): void => {
    setPermissions((prevPermissions) => {
      const nextId =
        prevPermissions.length > 0
          ? Math.min(0, ...prevPermissions.map((p) => p.id)) - 1
          : -1;
      return [...prevPermissions, { id: nextId, action: "", resource: "" }];
    });
  }, []);

  useEffect(() => {
    /** Fetches initial static data (actions, resources) and role prefill data if editing. */
    const fetchData = async () => {
      const fetchedData = await safeFetchInitialData(async () => {
        const actionsPromise = httpClient.request<ActionResource[]>(
          "/admin/action?app=1"
        );
        const resourcesPromise = httpClient.request<ActionResource[]>(
          "/admin/resource?app=1"
        );

        const id = roleId;
        let prefillPromise: Promise<Role[] | null>;
        if (id) {
          prefillPromise = httpClient.request<Role[]>(
            `/admin/role?app=1&id=${String(id)}`
          );
        } else {
          prefillPromise = Promise.resolve(null); // No prefill needed if creating
        }

        const [actionsRes, resourcesRes, prefillRes] = await Promise.all([
          actionsPromise,
          resourcesPromise,
          prefillPromise,
        ]);

        let prefillData: RolesFormPrefill;
        if (prefillRes && prefillRes.length > 0) {
          prefillData = {
            name: prefillRes[0].name,
            permissions: prefillRes[0].permissions,
          };
        } else if (id && (!prefillRes || prefillRes.length === 0)) {
          // If editing and no data found, throw error
          throw new Error("Role not found or empty response.");
        } else {
          // Creating new role
          prefillData = { name: "", permissions: [] };
        }

        return {
          actions: actionsRes,
          resources: resourcesRes,
          prefill: prefillData,
        };
      });

      if (fetchedData) {
        setActions(fetchedData.actions);
        setResources(fetchedData.resources);
        const prefillData = fetchedData.prefill;
        setName(prefillData.name);
        setPermissions(prefillData.permissions);
        // Add an initial permission row if creating and no permissions exist
        if (!roleId && prefillData.permissions.length === 0) {
          addPermission(); // Call addPermission here
        }
      } else {
        // Handle fetch error (message shown by hook)
        // Reset state or navigate back
        setName("");
        setPermissions([]);
        if (roleId) {
          // If editing failed to load, navigate back
          navigate(-1);
        } else if (!roleId) {
          addPermission(); // Still add permission if creating failed
        }
      }
    };

    void fetchData();
  }, [roleId, safeFetchInitialData, addPermission, navigate]);

  /**
   * Remove a permission and pair of action and resource dropdown menus
   * @param id - the database primary key
   */
  const removePermission = (id: number): void => {
    setPermissions((prevPermissions) =>
      prevPermissions.filter((p: Permission) => p.id !== id)
    );
  };

  /**
   * Select a new action for a given permission
   * @param actionId - the action's database primary key
   * @param permissionId - the permission's database primary key
   */
  const selectAction = (actionId: number, permissionId: number): void => {
    const action = actions.find((a: ActionResource) => a.id === actionId);

    if (action) {
      setPermissions((prevPermissions) =>
        prevPermissions.map((p: Permission) =>
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
    const action = actions.find(
      (a: ActionResource) => a.value === permission?.action
    );
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
      setPermissions((prevPermissions) =>
        prevPermissions.map((p: Permission) =>
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
    const resource = resources.find(
      (r: ActionResource) => r.value === permission?.resource
    );
    return resource ? resource.id : 0;
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async () => {
    // Filter out incomplete permissions and validate name
    const validPermissions = permissions
      .filter((p) => p.action && p.resource)
      .map((p: Permission) => ({
        action: p.action,
        resource: p.resource,
      }));

    if (!name.trim()) {
      flashMessage(<span>Role Name is required.</span>, "danger");
      return;
    }
    if (validPermissions.length === 0) {
      flashMessage(
        <span>
          At least one valid permission (Action + Resource) is required.
        </span>,
        "danger"
      );
      return;
    }

    // Construct the request body
    const data = { name: name.trim(), permissions: validPermissions };
    const id = roleId;
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data }),
    };

    const url = id ? "/admin/role/edit" : "/admin/role/create";

    await safeSubmit(() =>
      httpClient.request<ResponseBody>(url, {
        method: "POST",
        data: body,
      })
    );
  };

  /**
   * Compile the role's permissions as HTML for the entry summary
   * @returns - the permissions summary
   */
  const getPermissionsSummary = (): React.ReactElement => {
    return (
      <React.Fragment>
        {permissions
          .filter((p) => p.action || p.resource)
          .map((p: Permission, i) => {
            // Filter incomplete rows for summary
            // handle wildcard permissions
            const action =
              p.action === "*" ? "All Actions" : p.action || "[No Action]";
            const resource =
              p.resource === "*"
                ? "All Resources"
                : p.resource || "[No Resource]";

            return (
              <span key={`${p.id.toString()}-${i.toString()}`}>
                {" "}
                {/* Ensure unique key using index as well */}
                &nbsp;&nbsp;&nbsp;&nbsp;
                {action + " - " + resource}
                <br />
              </span>
            );
          })}
      </React.Fragment>
    );
  };

  // Use useCallback for permissionFields if dependencies are stable, otherwise useMemo
  const permissionFields = permissions.map((p: Permission) => (
    // Using p.id which can be negative for temporary rows
    <FormRow key={p.id} forceRow={true}>
      <FormField className="mr-4 xl:mr-8">
        <SelectField
          id={p.id} // Pass permission id
          opts={actions.map((a: ActionResource) => ({
            value: a.id,
            label: a.value,
          }))}
          placeholder="Action"
          callback={selectAction}
          getDefault={() => getSelectedAction(p.id)} // Pass id here
        />
      </FormField>
      <FormField>
        <SelectField
          id={p.id} // Pass permission id
          opts={resources.map((r: ActionResource) => ({
            value: r.id,
            label: r.value,
          }))}
          placeholder="Permission" // Should likely be "Resource"
          callback={selectResource}
          getDefault={() => getSelectedResource(p.id)} // Pass id here
        />
      </FormField>
      <div className="mb-8 flex cursor-pointer items-center px-2 lg:pr-4">
        <CloseIcon
          color="warning"
          fontSize="large"
          onClick={() => {
            removePermission(p.id);
          }}
        />
      </div>
    </FormRow>
  ));

  const buttonText = roleId ? "Update" : "Create";

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
        <FormTitle>{roleId ? "Edit " : "Create "} Role</FormTitle>
        <FormRow>
          <FormField>
            <TextField
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
          <span className="mb-1 px-4">Add Permissions to Role</span>
        </FormRow>
        {permissionFields}
        <FormRow>
          <FormField>
            <Button
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
        <FormSummaryTitle>Role Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name.trim() || "[No Name]"}
            <br />
            <br />
            Permissions:
            <br />
            {getPermissionsSummary()}
          </FormSummaryText>
          <FormSummaryButton onClick={post} disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
