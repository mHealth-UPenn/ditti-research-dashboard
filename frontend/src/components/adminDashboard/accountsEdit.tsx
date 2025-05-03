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

import React, { useEffect, useReducer } from "react";
import { Table } from "../table/table";
import { TableData } from "../table/table.types";
import { TextField } from "../fields/textField";
import { ToggleButton } from "../buttons/toggleButton";
import {
  AccessGroup,
  Account,
  ResponseBody,
  Role,
  Study,
} from "../../types/api";
import { SelectField } from "../fields/selectField";
import { httpClient } from "../../lib/http";
import { formatPhoneNumber } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormSummary } from "../containers/forms/formSummary";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import {
  AccountsEditState,
  AccountFormPrefill,
  RoleSelected,
} from "./adminDashboard.types";
import { useApiHandler } from "../../hooks/useApiHandler";

type Action =
  | {
      type: "INIT";
      accessGroups: AccessGroup[];
      roles: Role[];
      studies: Study[];
      prefill: AccountFormPrefill;
    }
  | {
      type: "EDIT_FIELD";
      firstName?: string;
      lastName?: string;
      email?: string;
      phoneNumber?: string;
    }
  | { type: "SELECT_ROLE"; roleId: number; studyId: number }
  | { type: "SELECT_ACCESS_GROUP"; id: number }
  | { type: "REMOVE_ACCESS_GROUP"; id: number }
  | { type: "SELECT_STUDY"; id: number }
  | { type: "REMOVE_STUDY"; id: number };

const reducer = (state: AccountsEditState, action: Action) => {
  switch (action.type) {
    case "INIT": {
      const { accessGroups, roles, studies, prefill } = action;
      return { ...state, accessGroups, roles, studies, ...prefill };
    }
    case "EDIT_FIELD": {
      const { firstName, lastName, email, phoneNumber } = action;
      if (firstName !== undefined) return { ...state, firstName };
      if (lastName !== undefined) return { ...state, lastName };
      if (email !== undefined) return { ...state, email };
      if (phoneNumber !== undefined) return { ...state, phoneNumber };
      return state;
    }
    case "SELECT_ROLE": {
      const { roleId, studyId } = action;

      // get all roles that have been selected for other studies
      const rolesSelected: RoleSelected[] = state.rolesSelected.filter(
        (x: RoleSelected) => x.study != studyId
      );

      // add this role
      rolesSelected.push({ study: studyId, role: roleId });
      return { ...state, rolesSelected };
    }
    case "SELECT_ACCESS_GROUP": {
      const { id } = action;
      const { accessGroups, accessGroupsSelected } = state;

      // get the access group
      const accessGroup = accessGroups.find((ag) => ag.id == id);
      if (
        accessGroup &&
        !accessGroupsSelected.some((ag) => ag.id === accessGroup.id)
      ) {
        // add it to the selected access groups
        return {
          ...state,
          accessGroupsSelected: [...accessGroupsSelected, accessGroup],
        };
      }
      return state;
    }
    case "REMOVE_ACCESS_GROUP": {
      const { id } = action;
      const accessGroupsSelected = state.accessGroupsSelected.filter(
        (ag) => ag.id != id
      );
      return { ...state, accessGroupsSelected };
    }
    case "SELECT_STUDY": {
      const { id } = action;
      const { studies, studiesSelected } = state;

      // get the study
      const study = studies.find((s: Study) => s.id == id);

      if (study && !studiesSelected.some((s) => s.id === study.id)) {
        // add it to the selected studies
        return { ...state, studiesSelected: [...studiesSelected, study] };
      }
      return state;
    }
    case "REMOVE_STUDY": {
      const { id } = action;
      const studiesSelected = state.studiesSelected.filter((s) => s.id != id);
      return { ...state, studiesSelected };
    }
    default:
      return state;
  }
};

const initialState: AccountsEditState = {
  accessGroups: [],
  roles: [],
  studies: [],
  firstName: "",
  lastName: "",
  email: "",
  phoneNumber: "",
  rolesSelected: [],
  accessGroupsSelected: [],
  studiesSelected: [],
};

// Define initial state for prefill within the component
const initialPrefillState: AccountFormPrefill = {
  firstName: "",
  lastName: "",
  email: "",
  phoneNumber: "",
  accessGroupsSelected: [],
  rolesSelected: [],
  studiesSelected: [],
};

export const AccountsEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const accountId = id ? parseInt(id) : 0;

  const [state, dispatch] = useReducer(reducer, initialState);
  const {
    accessGroups,
    roles,
    studies,
    firstName,
    lastName,
    email,
    phoneNumber,
    rolesSelected,
    accessGroupsSelected,
    studiesSelected,
  } = state;

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  // --- API Handlers ---
  const { safeRequest: safeFetchInitialData, isLoading: isLoadingData } =
    useApiHandler<{
      accessGroups: AccessGroup[];
      roles: Role[];
      studies: Study[];
      prefill: AccountFormPrefill;
    }>({
      errorMessage: "Failed to load initial account edit data.",
      showDefaultSuccessMessage: false,
    });

  const { safeRequest: safeSubmit, isLoading: isSubmitting } =
    useApiHandler<ResponseBody>({
      successMessage: (data) => data.msg,
      errorMessage: (error) => `Failed to save account: ${error.message}`,
      onSuccess: () => {
        navigate(-1); // Navigate back on success
      },
    });
  // --------------------

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body (should be Account[])
   * @returns - the form prefill data
   */
  const makePrefill = (res: Account[]): AccountFormPrefill => {
    const account = res[0];

    const roles = account.studies.map((s): RoleSelected => {
      return { study: s.id, role: s.role?.id ?? 0 };
    });

    return {
      firstName: account.firstName,
      lastName: account.lastName,
      email: account.email,
      phoneNumber: account.phoneNumber,
      accessGroupsSelected: account.accessGroups,
      rolesSelected: roles,
      studiesSelected: account.studies,
    };
  };

  useEffect(() => {
    const fetchData = async () => {
      const fetchedData = await safeFetchInitialData(async () => {
        const [accessGroupsRes, rolesRes, studiesRes] = await Promise.all([
          httpClient.request<AccessGroup[]>("/admin/access-group?app=1"),
          httpClient.request<Role[]>("/admin/role?app=1"),
          httpClient.request<Study[]>("/admin/study?app=1"),
        ]);

        let prefill: AccountFormPrefill;
        if (accountId) {
          // Fetch existing account data if editing
          const accountRes = await httpClient.request<Account[]>(
            `/admin/account?app=1&id=${String(accountId)}`
          );
          if (accountRes.length > 0) {
            prefill = makePrefill(accountRes);
          } else {
            throw new Error("Account not found or empty response.");
          }
        } else {
          // Use initial state if creating new
          prefill = initialPrefillState;
        }

        return {
          accessGroups: accessGroupsRes,
          roles: rolesRes,
          studies: studiesRes,
          prefill,
        };
      });

      if (fetchedData) {
        // Dispatch fetched data if successful
        dispatch({
          type: "INIT",
          accessGroups: fetchedData.accessGroups,
          roles: fetchedData.roles,
          studies: fetchedData.studies,
          prefill: fetchedData.prefill,
        });
      } else {
        // Handle fetch error (message shown by hook)
        if (accountId) {
          // If editing failed to load, navigate back
          navigate(-1);
        }
        // Reset state using dispatch to ensure consistency if not navigating back
        dispatch({
          // Dispatch action to reset state on error
          type: "INIT",
          accessGroups: initialState.accessGroups,
          roles: initialState.roles,
          studies: initialState.studies,
          prefill: initialPrefillState,
        });
      }
    };

    void fetchData();
  }, [accountId, safeFetchInitialData, navigate]);

  /**
   * Assign a role to the user for a given study
   * @param roleId - the role's database primary key
   * @param studyId - the study's database primary key
   */
  const selectRole = (roleId: number, studyId: number) => {
    dispatch({ type: "SELECT_ROLE", roleId, studyId });
  };

  /**
   * Get the assigned role for a given study
   * @param id - the study's database primary key
   * @returns - the role's database primary key
   */
  const getSelectedRole = (id: number) => {
    const roleSelected = rolesSelected.find((x) => x.study == id);
    return roleSelected?.role ?? 0;
  };

  /**
   * Assign a new access group to the user
   * @param id - the access group's database primary key
   */
  const addAccessGroup = (id: number): void => {
    dispatch({ type: "SELECT_ACCESS_GROUP", id });
  };

  /**
   * Remove an access group
   * @param id - the access group's database primary key
   */
  const removeAccessGroup = (id: number): void => {
    dispatch({ type: "REMOVE_ACCESS_GROUP", id });
  };

  /**
   * Assign a study to the user
   * @param id - the study's database primary key
   */
  const addStudy = (id: number): void => {
    dispatch({ type: "SELECT_STUDY", id });
  };

  /**
   * Remove a study
   * @param id - the study's database primary key
   */
  const removeStudy = (id: number): void => {
    dispatch({ type: "REMOVE_STUDY", id });
  };

  // Handle phone number input change
  const handlePhoneNumberChange = (value: string) => {
    const updatedPhoneNumber = formatPhoneNumber(value);
    dispatch({ type: "EDIT_FIELD", phoneNumber: updatedPhoneNumber });
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async () => {
    // Validate required fields
    if (!firstName.trim()) {
      flashMessage(
        <span>
          <b>First name is required</b>
        </span>,
        "danger"
      );
      return;
    }

    if (!lastName.trim()) {
      flashMessage(
        <span>
          <b>Last name is required</b>
        </span>,
        "danger"
      );
      return;
    }

    if (!email.trim()) {
      flashMessage(
        <span>
          <b>Email is required</b>
        </span>,
        "danger"
      );
      return;
    }

    // Validate phone number format if provided
    if (phoneNumber?.trim()) {
      // International phone numbers should start with + followed by at least 1 digit for country code
      // Country codes typically don't start with 0
      const phoneRegex = /^\+[1-9]\d*$/;
      if (!phoneRegex.test(phoneNumber)) {
        flashMessage(
          <span>
            <b>Invalid phone number format</b> - Phone number must start with +
            followed by country code and digits
          </span>,
          "danger"
        );
        return;
      }
    }

    // Construct studies data, ensuring role exists
    const studiesPayload = studiesSelected
      .map((s) => {
        const roleInfo = rolesSelected.find((r) => r.study === s.id);
        // Only include study if a role is selected
        return roleInfo ? { id: s.id, role: { id: roleInfo.role } } : null;
      })
      .filter((s): s is { id: number; role: { id: number } } => s !== null);

    if (
      studiesSelected.length > 0 &&
      studiesPayload.length !== studiesSelected.length
    ) {
      flashMessage(
        <span>Please assign a role to all selected studies.</span>,
        "danger"
      );
      return;
    }

    // Prepare account data for API submission
    const data = {
      access_groups: accessGroupsSelected.map((ag) => ({ id: ag.id })),
      email: email.trim(),
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      phone_number: phoneNumber?.trim() ?? "",
      studies: studiesPayload,
    };

    // Construct the request body
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(accountId ? { id: accountId, edit: data } : { create: data }),
    };

    const url = accountId ? "/admin/account/edit" : "/admin/account/create";

    // Use the API handler to submit the request
    await safeSubmit(() =>
      httpClient.request<ResponseBody>(url, {
        method: "POST",
        data: body,
      })
    );
  };

  /**
   * Compile the user's access groups as HTML for the entry summary
   * @returns - the user's access group summary
   */
  const getAccessGroupsSummary = () => {
    if (accessGroupsSelected.length === 0) {
      return <i>&nbsp;&nbsp;&nbsp;&nbsp;No access groups assigned.</i>;
    }
    return accessGroupsSelected.map((ag, i) => {
      // the permissions of each access group
      const permissions = ag.permissions.map((p, idx) => {
        const action = p.action == "*" ? "All Actions" : p.action;
        const resource = p.resource == "*" ? "All Resources" : p.resource;

        return (
          <span key={`${p.action}-${p.resource}-${String(idx)}`}>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            {action + " - " + resource}
            <br />
          </span>
        );
      });

      // each access group and its permissions
      return (
        <span key={ag.id}>
          {i > 0 && <br />}
          &nbsp;&nbsp;&nbsp;&nbsp;
          {ag.name}
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;Permissions:
          <br />
          {permissions}
        </span>
      );
    });
  };

  /**
   * Compile the user's studies as HTML for the entry summary
   * @returns - the user's study summary
   */
  const getStudiesSummary = () => {
    if (studiesSelected.length === 0) {
      return <i>&nbsp;&nbsp;&nbsp;&nbsp;No studies assigned.</i>;
    }

    return studiesSelected.map((s, i) => {
      let role: Role | undefined;
      let permissions: React.ReactElement[] = [];

      // get the selected role for each study
      const selectedRoleInfo: RoleSelected | undefined = rolesSelected.find(
        (sr: RoleSelected) => sr.study === s.id
      );

      if (selectedRoleInfo) {
        // get the selected role's data
        role = roles.find((r) => r.id === selectedRoleInfo.role);

        if (role?.permissions) {
          // list the permissions for each selected role
          permissions = role.permissions.map((p, idx) => {
            const action = p.action === "*" ? "All Actions" : p.action;
            const resource = p.resource === "*" ? "All Resources" : p.resource;

            return (
              <span key={`${p.action}-${p.resource}-${String(idx)}`}>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                {action + " - " + resource}
                <br />
              </span>
            );
          });
        }
      }

      // list each study, its assigned role, and the role's permissions
      return (
        <span key={s.id}>
          {i > 0 && <br />}
          &nbsp;&nbsp;&nbsp;&nbsp;
          {s.name}
          <br />
          <span>
            &nbsp;&nbsp;&nbsp;&nbsp;Role:
            {role?.name ? ` ${role.name}` : ` [No Role Assigned]`}
            <br />
            {permissions.length > 0 && permissions}
          </span>
        </span>
      );
    });
  };

  const buttonText = accountId ? "Update" : "Create";

  const columnsAccessGroups = [
    {
      name: "Name",
      sortable: true,
      searchable: false,
      width: 43,
    },
    {
      name: "App",
      sortable: true,
      searchable: false,
      width: 43,
    },
    {
      name: "Added",
      sortable: true,
      searchable: false,
      width: 14,
    },
  ];

  const columnsStudies = [
    {
      name: "Name",
      sortable: true,
      searchable: false,
      width: 43,
    },
    {
      name: "Role",
      sortable: false,
      searchable: false,
      width: 43,
    },
    {
      name: "Added",
      sortable: true,
      searchable: false,
      width: 14,
    },
  ];

  const accessGroupsData: TableData[][] = accessGroups.map((ag) => {
    const selected = accessGroupsSelected.some((sag) => sag.id === ag.id);
    return [
      {
        contents: <span>{ag.name}</span>,
        searchValue: "",
        sortValue: ag.name,
      },
      {
        contents: <span>{ag.app.name}</span>,
        searchValue: "",
        sortValue: ag.app.name,
      },
      {
        contents: (
          <ToggleButton
            key={ag.id}
            id={ag.id}
            active={selected}
            add={addAccessGroup}
            remove={removeAccessGroup}
            fullWidth={true}
            fullHeight={true}
          />
        ),
        searchValue: "",
        sortValue: selected ? 1 : 0,
        paddingX: 0,
        paddingY: 0,
      },
    ];
  });

  const studiesData = studies.map((s) => {
    const selected = studiesSelected.some((ss) => ss.id === s.id);
    return [
      {
        contents: (
          <div className="flex-left table-data">
            <span>{s.name}</span>
          </div>
        ),
        searchValue: "",
        sortValue: s.name,
      },
      {
        contents: (
          <SelectField
            key={s.id}
            id={s.id}
            opts={roles.map((r: Role) => ({ value: r.id, label: r.name }))}
            placeholder="Select role..."
            callback={selectRole}
            getDefault={getSelectedRole}
            hideBorder={true}
          />
        ),
        searchValue: "",
        sortValue: "",
        paddingX: 0,
        paddingY: 0,
      },
      {
        contents: (
          <ToggleButton
            key={s.id}
            id={s.id}
            active={selected}
            add={addStudy}
            remove={removeStudy}
            fullWidth={true}
            fullHeight={true}
          />
        ),
        searchValue: "",
        sortValue: selected ? 1 : 0,
        paddingX: 0,
        paddingY: 0,
      },
    ];
  });

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
        <FormTitle>{accountId ? "Edit " : "Create "} Account</FormTitle>
        <FormRow>
          <FormField>
            <TextField
              id="first-name"
              type="text"
              placeholder=""
              value={firstName}
              label="First Name"
              onKeyup={(firstName) => {
                dispatch({ type: "EDIT_FIELD", firstName });
              }}
              feedback=""
            />
          </FormField>
          <FormField>
            <TextField
              id="last-name"
              type="text"
              placeholder=""
              value={lastName}
              label="Last Name"
              onKeyup={(lastName) => {
                dispatch({ type: "EDIT_FIELD", lastName });
              }}
              feedback=""
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <TextField
              id="email"
              type="text"
              placeholder=""
              value={email}
              label="Email"
              onKeyup={
                accountId
                  ? undefined
                  : (email) => {
                      dispatch({ type: "EDIT_FIELD", email });
                    }
              }
              feedback=""
              disabled={!!accountId}
            />
          </FormField>
          <FormField>
            <TextField
              id="phoneNumber"
              type="text"
              placeholder=""
              value={phoneNumber ?? ""}
              label="Phone Number"
              onKeyup={handlePhoneNumberChange}
              feedback={
                phoneNumber?.trim() && !/^\+[1-9]\d*$/.test(phoneNumber)
                  ? "Phone number must start with + followed by country code and digits"
                  : ""
              }
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <span className="mb-1">Assign Account to Access Group</span>
            <Table
              columns={columnsAccessGroups}
              control={<React.Fragment />}
              controlWidth={0}
              data={accessGroupsData}
              includeControl={false}
              includeSearch={false}
              paginationPer={4}
              sortDefault="Name"
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <span className="mb-1">Assign Account to Studies</span>
            <Table
              columns={columnsStudies}
              control={<React.Fragment />}
              controlWidth={0}
              data={studiesData}
              includeControl={false}
              includeSearch={false}
              paginationPer={4}
              sortDefault="Name"
            />
          </FormField>
        </FormRow>
      </Form>
      <FormSummary>
        <FormSummaryTitle>Account Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;
            {firstName || lastName ? `${firstName} ${lastName}` : <i>Name</i>}
            <br />
            <br />
            Email:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;
            {email ? email : <i>Email</i>}
            <br />
            <br />
            AccessGroups:
            <br />
            {getAccessGroupsSummary()}
            <br />
            Studies:
            <br />
            {getStudiesSummary()}
            <br />
          </FormSummaryText>
          <FormSummaryButton onClick={post} disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
