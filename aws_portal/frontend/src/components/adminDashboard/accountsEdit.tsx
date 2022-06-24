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
  Study
} from "../../interfaces";
import Select from "../fields/select";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";

interface AccountsEditProps {
  accountId: number;
}

interface RoleSelected {
  study: number;
  role: number;
}

interface AccountPrefill {
  email: string;
  firstName: string;
  lastName: string;
  accessGroupsSelected: AccessGroup[];
  rolesSelected: RoleSelected[];
  studiesSelected: Study[];
}

interface AccountsEditState extends AccountPrefill {
  accessGroups: AccessGroup[];
  roles: Role[];
  studies: Study[];
  columnsAccessGroups: Column[];
  columnsStudies: Column[];
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
        width: 30
      },
      {
        name: "Access Group",
        sortable: true,
        searchable: false,
        width: 30
      },
      {
        name: "Role",
        sortable: false,
        searchable: false,
        width: 30
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
    rolesSelected: [],
    accessGroupsSelected: [],
    studiesSelected: []
  };

  componentDidMount() {
    const accessGroups = makeRequest("/admin/access-group?app=1").then(
      (accessGroups: AccessGroup[]) => this.setState({ accessGroups })
    );
    const roles = makeRequest("/admin/role?app=1").then((roles: Role[]) =>
      this.setState({ roles })
    );
    const studies = makeRequest("/admin/study?app=1").then((studies: Study[]) =>
      this.setState({ studies })
    );
    const prefill = this.getPrefill().then((prefill: AccountPrefill) =>
      this.setState({ ...prefill })
    );

    const promises = [accessGroups, roles, studies, prefill];
    Promise.all(promises).then(() => this.setState({ loading: false }));
  }

  getPrefill = async (): Promise<AccountPrefill> => {
    const id = this.props.accountId;
    return id
      ? makeRequest("/admin/account?app=1&id=" + id).then(this.makePrefill)
      : {
          firstName: "",
          lastName: "",
          email: "",
          accessGroupsSelected: [],
          rolesSelected: [],
          studiesSelected: []
        };
  };

  makePrefill = (res: Account[]): AccountPrefill => {
    const account = res[0];
    const roles = account.studies.map((s): RoleSelected => {
      return { study: s.id, role: s.role.id };
    });

    return {
      firstName: account.firstName,
      lastName: account.lastName,
      email: account.email,
      accessGroupsSelected: account.accessGroups,
      rolesSelected: roles,
      studiesSelected: account.studies
    };
  };

  getAccessGroupsData = (): TableData[][] => {
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

  getStudiesData = (): TableData[][] => {
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
            <div className="flex-left table-data">
              <span>accessGroup</span>
            </div>
          ),
          searchValue: "",
          sortValue: "accessGroup"
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

  selectRole = (roleId: number, studyId: number): void => {
    const rolesSelected: RoleSelected[] = this.state.rolesSelected.filter(
      (x: RoleSelected) => x.study != studyId
    );
    rolesSelected.push({ study: studyId, role: roleId });
    this.setState({ rolesSelected });
  };

  getSelectedRole = (id: number) => {
    const { rolesSelected } = this.state;
    if (rolesSelected.some((x: RoleSelected) => x.study == id)) {
      const roleSelected: RoleSelected = rolesSelected.filter(
        (x: RoleSelected) => x.study == id
      )[0];
      return roleSelected.role;
    } else {
      return 0;
    }
  };

  isActiveAccessGroup = (id: number): boolean => {
    return this.state.accessGroupsSelected.some(
      (ag: AccessGroup) => ag.id == id
    );
  };

  addAccessGroup = (id: number, callback: () => void): void => {
    const { accessGroups, accessGroupsSelected } = this.state;
    const accessGroup = accessGroups.filter(
      (ag: AccessGroup) => ag.id == id
    )[0];

    if (accessGroup) {
      accessGroupsSelected.push(accessGroup);
      this.setState({ accessGroupsSelected }, callback);
    }
  };

  removeAccessGroup = (id: number, callback: () => void): void => {
    const accessGroupsSelected = this.state.accessGroupsSelected.filter(
      (ag: AccessGroup) => ag.id != id
    );
    this.setState({ accessGroupsSelected }, callback);
  };

  isActiveStudy = (id: number): boolean => {
    return this.state.studiesSelected.some((s: Study) => s.id == id);
  };

  addStudy = (id: number, callback: () => void): void => {
    const { studies, studiesSelected } = this.state;
    const study = Object.assign(
      {},
      studies.filter((s: Study) => s.id == id)[0]
    );

    if (study) {
      studiesSelected.push(study);
      this.setState({ studiesSelected }, callback);
    }
  };

  removeStudy = (id: number, callback: () => void): void => {
    const studiesSelected = this.state.studiesSelected.filter(
      (s: Study) => s.id != id
    );
    this.setState({ studiesSelected }, callback);
  };

  post = (): void => {
    const {
      accessGroupsSelected,
      email,
      firstName,
      lastName,
      rolesSelected,
      studiesSelected
    } = this.state;

    const accessGroups = accessGroupsSelected.map((ag: AccessGroup) => {
      return { id: ag.id };
    });

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
      studies: studies
    };

    const id = this.props.accountId;
    const body = {
      app: 1,
      ...(id ? { id: id, edit: data } : { create: data })
    };
    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/account/edit" : "/admin/account/create";
    makeRequest(url, opts).then(this.handleSuccess).catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    console.log(res.msg);
  };

  handleFailure = (res: ResponseBody) => {
    console.log(res.msg);
  };

  getAccessGroupsSummary = () => {
    return this.state.accessGroupsSelected.map((ag: AccessGroup, i) => {
      const permissions = ag.permissions.map((p: Permission, i: number) => {
        return (
          <span key={i}>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            {p.action + " - " + p.resource}
            <br />
          </span>
        );
      });

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

  getStudiesSummary = () => {
    let role: Role;
    let permissions: React.ReactElement[];
    const { roles, rolesSelected, studiesSelected } = this.state;

    return studiesSelected.map((s: Study, i) => {
      role = {} as Role;
      permissions = [<React.Fragment key={0} />];

      const selectedRole: RoleSelected = rolesSelected.filter(
        (sr: RoleSelected) => sr.study == s.id
      )[0];

      if (selectedRole) {
        role = roles.filter((r: Role) => r.id == selectedRole.role)[0];

        if (role) {
          permissions = role.permissions.map((p, j) => {
            return (
              <span key={j}>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                {p.action + " - " + p.resource}
                <br />
              </span>
            );
          });
        }
      }

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
      firstName,
      lastName
    } = this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {accountId ? "Edit " : "Create "} Account
              </h1>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="first-name"
                    svg={<React.Fragment />}
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
                    svg={<React.Fragment />}
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
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={email}
                    label="Email"
                    onKeyup={(text: string) => this.setState({ email: text })}
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <span>Assign Account to Access Group</span>
                  {loading ? (
                    <SmallLoader />
                  ) : (
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
                  )}
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <span>Assign Account to Studies</span>
                  {loading ? (
                    <SmallLoader />
                  ) : (
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
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Account Summary</h1>
          <span>
            {firstName || lastName ? firstName + " " + lastName : <i>Name</i>}
            <br />
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
          {accountId ? (
            <button className="button-primary" onClick={this.post}>
              Update
            </button>
          ) : (
            <button className="button-primary" onClick={this.post}>
              Create
            </button>
          )}
        </div>
      </div>
    );
  }
}

export default AccountsEdit;
