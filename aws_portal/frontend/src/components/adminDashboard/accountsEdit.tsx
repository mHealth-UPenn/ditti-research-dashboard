import * as React from "react";
import { Component } from "react";
import Table, { Column, TableData } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";
import {
  AccessGroup,
  Account,
  Permission,
  ResponseBody,
  Role,
  Study,
  ViewProps
} from "../../interfaces";
import Select from "../fields/select";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

/**
 * accountId: the database primary key, 0 if creating a new entry
 */
interface AccountsEditProps extends ViewProps {
  accountId: number;
}

/**
 * study: the database primary key of study the role is selected for
 * role: the role's database primary key
 */
interface RoleSelected {
  study: number;
  role: number;
}

/**
 * the form's prefill
 */
interface AccountPrefill {
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
  accessGroupsSelected: AccessGroup[];
  rolesSelected: RoleSelected[];
  studiesSelected: Study[];
}

/**
 * accessGroups: all available access groups for selection
 * roles: all available roles for selection
 * studies: all available studies for selection
 * columnsAccessGroups: columns for the access groups table
 * columnsStudies: columns for the studies table
 * password: the password to be set
 * loading: whether to show the loader
 */
interface AccountsEditState extends AccountPrefill {
  accessGroups: AccessGroup[];
  roles: Role[];
  studies: Study[];
  columnsAccessGroups: Column[];
  columnsStudies: Column[];
  password: string;
  loading: boolean;
}

class AccountsEdit extends React.Component<
  AccountsEditProps,
  AccountsEditState
> {
  state = {
    accessGroups: [],
    roles: [],
    studies: [],
    columnsAccessGroups: [
      {
        name: "Name",
        sortable: true,
        searchable: false,
        width: 45
      },
      {
        name: "App",
        sortable: true,
        searchable: false,
        width: 45
      },
      {
        name: "",
        sortable: false,
        searchable: false,
        width: 10
      }
    ],
    columnsStudies: [
      {
        name: "Name",
        sortable: true,
        searchable: false,
        width: 45
      },
      {
        name: "Role",
        sortable: false,
        searchable: false,
        width: 45
      },
      {
        name: "",
        sortable: false,
        searchable: false,
        width: 10
      }
    ],
    loading: true,
    firstName: "",
    lastName: "",
    email: "",
    phoneNumber: "",
    rolesSelected: [],
    accessGroupsSelected: [],
    studiesSelected: [],
    password: ""
  };

  componentDidMount() {

    // get all access groups
    const accessGroups = makeRequest("/admin/access-group?app=1").then(
      (accessGroups: AccessGroup[]) => this.setState({ accessGroups })
    );

    // get all roles
    const roles = makeRequest("/admin/role?app=1").then((roles: Role[]) =>
      this.setState({ roles })
    );

    // get all studies
    const studies = makeRequest("/admin/study?app=1").then((studies: Study[]) =>
      this.setState({ studies })
    );

    // set the form prefill data
    const prefill = this.getPrefill().then((prefill: AccountPrefill) =>
      this.setState({ ...prefill })
    );

    // when all requests are complete, hide the loader
    const promises = [accessGroups, roles, studies, prefill];
    Promise.all(promises).then(() => this.setState({ loading: false }));
  }

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  getPrefill = async (): Promise<AccountPrefill> => {
    const id = this.props.accountId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/account?app=1&id=" + id).then(this.makePrefill)
      : {
          firstName: "",
          lastName: "",
          email: "",
          phoneNumber: "",
          accessGroupsSelected: [],
          rolesSelected: [],
          studiesSelected: []
        };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  makePrefill = (res: Account[]): AccountPrefill => {
    const account = res[0];
    const roles = account.studies.map((s): RoleSelected => {
      return { study: s.id, role: s.role.id };
    });

    return {
      firstName: account.firstName,
      lastName: account.lastName,
      email: account.email,
      phoneNumber: account.phoneNumber,
      accessGroupsSelected: account.accessGroups,
      rolesSelected: roles,
      studiesSelected: account.studies
    };
  };

  /**
   * Get the contents for the access groups table
   * @returns - the table contents
   */
  getAccessGroupsData = (): TableData[][] => {

    // map each table row to table cells for each column
    return this.state.accessGroups.map((ag: AccessGroup) => {
      const { id, name, app } = ag;

      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: "",
          sortValue: name
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{app.name}</span>
            </div>
          ),
          searchValue: "",
          sortValue: app.name
        },
        {
          contents: (
            <div className="flex-left table-control">
              <ToggleButton
                key={id}
                id={id}
                getActive={this.isActiveAccessGroup}
                add={this.addAccessGroup}
                remove={this.removeAccessGroup}
              />
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  /**
   * Get the contents for the studies table
   * @returns - the table contents
   */
  getStudiesData = (): TableData[][] => {

    // map each table row to table cells for each column
    return this.state.studies.map((s) => {
      const { id, name } = s;

      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: "",
          sortValue: name
        },
        {
          contents: (
            <div className="flex-left" style={{ position: "relative" }}>
              <Select
                key={id}
                id={id}
                opts={this.state.roles.map((r: Role) => {
                  return { value: r.id, label: r.name };
                })}
                placeholder="Select role..."
                callback={this.selectRole}
                getDefault={this.getSelectedRole}
              />
            </div>
          ),
          searchValue: "",
          sortValue: ""
        },
        {
          contents: (
            <div className="flex-left table-control">
              <ToggleButton
                key={id}
                id={id}
                getActive={this.isActiveStudy}
                add={this.addStudy}
                remove={this.removeStudy}
              />
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  /**
   * Assign a role to the user for a given study
   * @param roleId - the role's database primary key
   * @param studyId - the study's database primary key
   */
  selectRole = (roleId: number, studyId: number): void => {

    // get all roles that have been selected for other studies
    const rolesSelected: RoleSelected[] = this.state.rolesSelected.filter(
      (x: RoleSelected) => x.study != studyId
    );

    // add this role
    rolesSelected.push({ study: studyId, role: roleId });
    this.setState({ rolesSelected });
  };

  /**
   * Get the assigned role for a given study
   * @param id - the study's database primary key
   * @returns - the role's database primary key
   */
  getSelectedRole = (id: number) => {
    const { rolesSelected } = this.state;

    if (rolesSelected.some((x: RoleSelected) => x.study == id)) {

      // get the role selected for this study
      const roleSelected: RoleSelected = rolesSelected.filter(
        (x: RoleSelected) => x.study == id
      )[0];

      return roleSelected.role;
    } else {
      return 0;
    }
  };

  /**
   * Check if a given access group is currently assigned to the user
   * @param id - the database primary key of the access group to check
   * @returns - whether the access group is selected
   */
  isActiveAccessGroup = (id: number): boolean => {
    return this.state.accessGroupsSelected.some(
      (ag: AccessGroup) => ag.id == id
    );
  };

  /**
   * Assign a new access group to the user
   * @param id - the access group's database primary key
   * @param callback
   */
  addAccessGroup = (id: number, callback: () => void): void => {
    const { accessGroups, accessGroupsSelected } = this.state;

    // get the access group
    const accessGroup = accessGroups.filter(
      (ag: AccessGroup) => ag.id == id
    )[0];

    if (accessGroup) {

      // add it to the selected access groups
      accessGroupsSelected.push(accessGroup);
      this.setState({ accessGroupsSelected }, callback);
    }
  };

  /**
   * Remove an access group
   * @param id - the access group's database primary key
   * @param callback 
   */
  removeAccessGroup = (id: number, callback: () => void): void => {
    const accessGroupsSelected = this.state.accessGroupsSelected.filter(
      (ag: AccessGroup) => ag.id != id
    );

    this.setState({ accessGroupsSelected }, callback);
  };

  /**
   * Check a given study is assigned to the user
   * @param id - the study's database primary key
   * @returns - whether the study is assigned to the user
   */
  isActiveStudy = (id: number): boolean => {
    return this.state.studiesSelected.some((s: Study) => s.id == id);
  };

  /**
   * Assign a study to the user
   * @param id - the study's database primary key
   * @param callback 
   */
  addStudy = (id: number, callback: () => void): void => {
    const { studies, studiesSelected } = this.state;

    // get the study
    const study = Object.assign(
      {},
      studies.filter((s: Study) => s.id == id)[0]
    );

    if (study) {

      // add it to the selected studies
      studiesSelected.push(study);
      this.setState({ studiesSelected }, callback);
    }
  };

  /**
   * Remove a study
   * @param id - the study's database primary key
   * @param callback 
   */
  removeStudy = (id: number, callback: () => void): void => {
    const studiesSelected = this.state.studiesSelected.filter(
      (s: Study) => s.id != id
    );

    this.setState({ studiesSelected }, callback);
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  post = async (): Promise<void> => {
    const {
      accessGroupsSelected,
      email,
      firstName,
      lastName,
      phoneNumber,
      rolesSelected,
      studiesSelected,
      password
    } = this.state;

    // get all access groups that are assigned to the user
    const accessGroups = accessGroupsSelected.map((ag: AccessGroup) => {
      return { id: ag.id };
    });

    // get all studies and roles that are assigned to the user
    const studies = studiesSelected.map((s: Study) => {
      const role: RoleSelected = rolesSelected.filter(
        (r: RoleSelected) => r.study == s.id
      )[0];
      return { id: s.id, role: role ? { id: role.role } : {} };
    });

    const data = {
      access_groups: accessGroups,
      email: email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber,
      studies: studies,
      password: password
    };

    const id = this.props.accountId;
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/account/edit" : "/admin/account/create";

    await makeRequest(url, opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  handleSuccess = (res: ResponseBody) => {
    const { flashMessage, goBack } = this.props;

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
   * Compile the user's access groups as HTML for the entry summary
   * @returns - the user's access group summary
   */
  getAccessGroupsSummary = () => {
    return this.state.accessGroupsSelected.map((ag: AccessGroup, i) => {

      // the permissions of each access group
      const permissions = ag.permissions.map((p: Permission, i: number) => {
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
  getStudiesSummary = () => {
    let role: Role;
    let permissions: React.ReactElement[];
    const { roles, rolesSelected, studiesSelected } = this.state;

    return studiesSelected.map((s: Study, i) => {
      role = {} as Role;
      permissions = [<React.Fragment key={0} />];

      // get the selected role for each study
      const selectedRole: RoleSelected = rolesSelected.filter(
        (sr: RoleSelected) => sr.study == s.id
      )[0];

      if (selectedRole) {

        // get the selected role's data
        role = roles.filter((r: Role) => r.id == selectedRole.role)[0];

        if (role) {

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
          {role ? (
            <span>
              &nbsp;&nbsp;&nbsp;&nbsp;Role:
              {role.name ? " " + role.name : " " + "unassigned"}
              <br />
              {permissions}
            </span>
          ) : null}
        </span>
      );
    });
  };

  render() {
    const { accountId } = this.props;
    const {
      columnsAccessGroups,
      columnsStudies,
      loading,
      email,
      phoneNumber,
      firstName,
      lastName
    } = this.state;

    const buttonText = accountId ? "Update" : "Create";

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
                  {accountId ? "Edit " : "Create "} Account
                </h1>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="first-name"
                      type="text"
                      placeholder=""
                      prefill={firstName}
                      label="First Name"
                      onKeyup={(text: string) =>
                        this.setState({ firstName: text })
                      }
                      feedback=""
                    />
                  </div>
                  <div className="admin-form-field">
                    <TextField
                      id="last-name"
                      type="text"
                      placeholder=""
                      prefill={lastName}
                      label="Last Name"
                      onKeyup={(text: string) =>
                        this.setState({ lastName: text })
                      }
                      feedback=""
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="email"
                      type="text"
                      placeholder=""
                      prefill={email}
                      label="Email"
                      onKeyup={(text: string) => this.setState({ email: text })}
                      feedback=""
                    />
                  </div>
                  <div className="admin-form-field">
                    <TextField
                      id="phoneNumber"
                      type="text"
                      placeholder=""
                      prefill={phoneNumber}
                      label="Phone Number"
                      onKeyup={(text: string) =>
                        this.setState({ phoneNumber: text })
                      }
                      feedback=""
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="password"
                      type="password"
                      label={accountId ? "Change password" : "Password"}
                      onKeyup={(text: string) =>
                        this.setState({ password: text })
                      }
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <span>Assign Account to Access Group</span>
                    <Table
                      columns={columnsAccessGroups}
                      control={<React.Fragment />}
                      controlWidth={0}
                      data={this.getAccessGroupsData()}
                      includeControl={false}
                      includeSearch={false}
                      paginationPer={4}
                      sortDefault="Name"
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <span>Assign Account to Studies</span>
                    <Table
                      columns={columnsStudies}
                      control={<React.Fragment />}
                      controlWidth={0}
                      data={this.getStudiesData()}
                      includeControl={false}
                      includeSearch={false}
                      paginationPer={4}
                      sortDefault="Name"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="admin-form-summary bg-dark">

          {/* the edit/create summary */}
          <h1 className="border-white-b">Account Summary</h1>
          <span>
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
            {this.getAccessGroupsSummary()}
            <br />
            Studies:
            <br />
            {this.getStudiesSummary()}
            <br />
          </span>
          <AsyncButton onClick={this.post} text={buttonText} type="primary" />
        </div>
      </div>
    );
  }
}

export default AccountsEdit;
