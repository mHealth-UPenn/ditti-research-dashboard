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

import React, { useEffect, useReducer, useCallback } from "react";
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
import { formatPhoneNumber } from "../../utils";
import { useHttpClient } from "../../lib/HttpClientContext";
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
import { HttpError } from "../../lib/http.types";

type Action =
  | {
      type: "INIT";
      accessGroups: AccessGroup[];
      roles: Role[];
      studies: Study[];
      prefill: AccountFormPrefill;
      loading: boolean;
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
      const { accessGroups, roles, studies, prefill, loading } = action;
      return { ...state, accessGroups, roles, studies, loading, ...prefill };
    }
    case "EDIT_FIELD": {
      const { firstName, lastName, email, phoneNumber } = action;
      if (firstName) return { ...state, firstName };
      if (lastName) return { ...state, lastName };
      if (email) return { ...state, email };
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
        accessGroupsSelected.push(accessGroup);
        return { ...state, accessGroupsSelected };
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
      const study = Object.assign(
        {},
        studies.find((s: Study) => s.id == id)
      );

      if (!studiesSelected.some((s) => s.id === study.id)) {
        // add it to the selected studies
        studiesSelected.push(study);
        return { ...state, studiesSelected };
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
  loading: true,
  firstName: "",
  lastName: "",
  email: "",
  phoneNumber: "",
  rolesSelected: [],
  accessGroupsSelected: [],
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
    loading,
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
  const { request } = useHttpClient();

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = useCallback(async (): Promise<AccountFormPrefill> => {
    // if editing an existing entry, return prefill data, else return empty data
    return accountId
      ? request<Account[]>(`/admin/account?app=1&id=${String(accountId)}`).then(
          (res) => makePrefill(res)
        )
      : {
          firstName: "",
          lastName: "",
          email: "",
          phoneNumber: "",
          accessGroupsSelected: [],
          rolesSelected: [],
          studiesSelected: [],
        };
  }, [accountId, request]);

  useEffect(() => {
    // when all requests are complete, initialize the state
    const fetchData = async () => {
      try {
        const [accessGroups, roles, studies, prefill] = await Promise.all([
          request<AccessGroup[]>(`/admin/access-group?app=1`),
          request<Role[]>(`/admin/role?app=1`),
          request<Study[]>(`/admin/study?app=1`),
          getPrefill(),
        ]);

        dispatch({
          type: "INIT",
          accessGroups,
          roles,
          studies,
          prefill,
          loading: false,
        });
      } catch (error) {
        console.error("Failed to fetch data:", error);
        // Handle error as needed
      }
    };

    void fetchData();
  }, [getPrefill, request]);

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
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
    if (rolesSelected.some((x) => x.study == id)) {
      // get the role selected for this study
      const roleSelected = rolesSelected.find((x) => x.study == id);
      return roleSelected?.role ?? 0;
    }
    return 0;
  };

  /**
   * Assign a new access group to the user
   * @param id - the access group's database primary key
   * @param callback
   */
  const addAccessGroup = (id: number): void => {
    dispatch({ type: "SELECT_ACCESS_GROUP", id });
  };

  /**
   * Remove an access group
   * @param id - the access group's database primary key
   * @param callback
   */
  const removeAccessGroup = (id: number): void => {
    dispatch({ type: "REMOVE_ACCESS_GROUP", id });
  };

  /**
   * Assign a study to the user
   * @param id - the study's database primary key
   * @param callback
   */
  const addStudy = (id: number): void => {
    dispatch({ type: "SELECT_STUDY", id });
  };

  /**
   * Remove a study
   * @param id - the study's database primary key
   * @param callback
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
  const post = async (): Promise<void> => {
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

    // Construct studies data structure with role assignments
    const studies = studiesSelected.map((s) => {
      const role = rolesSelected.find((r) => r.study == s.id);
      return { id: s.id, role: role ? { id: role.role } : {} };
    });

    // Prepare account data for API submission
    const data = {
      access_groups: accessGroupsSelected,
      email: email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber ?? "", // Always send phone_number, empty string signals deletion
      studies: studies,
    };

    // Determine if this is an edit or create operation
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(accountId ? { id: accountId, edit: data } : { create: data }),
    };

    const opts = { method: "POST", data: body };
    const url = accountId ? "/admin/account/edit" : "/admin/account/create";

    try {
      const res = await request<ResponseBody>(url, opts);
      handleSuccess(res);
    } catch (error) {
      handleFailure(error);
    }
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
   * @param error - the error object
   */
  const handleFailure = (error: unknown) => {
    let displayMessage = "Internal server error";
    if (error instanceof HttpError && error.apiError?.data) {
      displayMessage = error.apiError.data.msg;
    } else if (error instanceof Error) {
      displayMessage = error.message;
    }
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {displayMessage}
      </span>
    );

    flashMessage(msg, "danger");
  };

  /**
   * Compile the user's access groups as HTML for the entry summary
   * @returns - the user's access group summary
   */
  const getAccessGroupsSummary = () => {
    return accessGroupsSelected.map((ag, i) => {
      // the permissions of each access group
      const permissions = ag.permissions.map((p, i) => {
        const action = p.action == "*" ? "All Actions" : p.action;
        const resource = p.resource == "*" ? "All Resources" : p.resource;

        return (
          <span key={i}>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            {action + " - " + resource}
            <br />
          </span>
        );
      });

      // each access group and its permissions
      return (
        <span key={i}>
          {i ? <br /> : ""}
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
    let role: Role | undefined;
    let permissions: React.ReactElement[];

    return studiesSelected.map((s, i) => {
      role = {} as Role;
      permissions = [<React.Fragment key={0} />];

      // get the selected role for each study
      const selectedRole: RoleSelected | undefined = rolesSelected.find(
        (sr: RoleSelected) => sr.study == s.id
      );

      if (selectedRole) {
        // get the selected role's data
        role = roles.find((r) => r.id == selectedRole.role);

        if (role?.permissions) {
          // list the permissions for each selected role
          permissions = role.permissions.map((p, j) => {
            const action = p.action == "*" ? "All Actions" : p.action;
            const resource = p.resource == "*" ? "All Resources" : p.resource;

            return (
              <span key={j}>
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
        <span key={i}>
          {i ? <br /> : ""}
          &nbsp;&nbsp;&nbsp;&nbsp;
          {s.name}
          <br />
          {role && (
            <span>
              &nbsp;&nbsp;&nbsp;&nbsp;Role:
              {role.name ? " " + role.name : " " + "unassigned"}
              <br />
              {permissions}
            </span>
          )}
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
    const selected = accessGroupsSelected.some((sag) => sag.id == ag.id);
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
    const selected = studiesSelected.some((ss) => ss.id == s.id);
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
              disabled={accountId ? true : false}
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
            {firstName || lastName ? firstName + " " + lastName : <i>Name</i>}
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
          <FormSummaryButton onClick={post}>{buttonText}</FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
