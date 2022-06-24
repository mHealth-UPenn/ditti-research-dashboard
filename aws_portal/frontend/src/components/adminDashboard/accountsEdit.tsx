import * as React from "react";
import { Component } from "react";
import Table, { Column, TableData } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";
import { AccessGroup, ResponseBody, Role, Study } from "../../interfaces";
import Select from "../fields/select";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";

interface AccountsEditProps {
  accountId: number;
}

interface AccountsEditState {
  accessGroups: AccessGroup[];
  roles: Role[];
  studies: Study[];
  columnsAccessGroups: Column[];
  columnsStudies: Column[];
  loading: boolean;
  fading: boolean;
  email: string;
  firstName: string;
  lastName: string;
  accessGroupsSelected: AccessGroup[];
  rolesSelected: { study: number; role: number }[];
  studiesSelected: Study[];
}

class AccountsEdit extends React.Component<
  AccountsEditProps,
  AccountsEditState
> {
  constructor(props: AccountsEditProps) {
    super(props);

    const { accountId } = props;
    const prefill = accountId
      ? this.getPrefill(accountId)
      : {
          email: "",
          firstName: "",
          lastName: "",
          accessGroupsSelected: [],
          rolesSelected: [],
          studiesSelected: []
        };

    this.state = {
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
      fading: false,
      firstName: prefill.firstName,
      lastName: prefill.lastName,
      email: prefill.email,
      rolesSelected: prefill.rolesSelected,
      accessGroupsSelected: prefill.accessGroupsSelected,
      studiesSelected: prefill.studiesSelected
    };
  }

  getPrefill(id: number) {
    return {
      firstName: "",
      lastName: "",
      email: "",
      accessGroupsSelected: [],
      rolesSelected: [],
      studiesSelected: []
    };
  }

  componentDidMount() {
    const accessGroups = makeRequest("/admin/access-group?app=1");
    const roles = makeRequest("/admin/role?app=1");
    const studies = makeRequest("/admin/study?app=1");
    const promises = [accessGroups, roles, studies];

    Promise.all(promises).then((value) => {
      const [accessGroups, roles, studies] = value;

      this.setState({
        accessGroups,
        roles,
        studies,
        loading: false,
        fading: true
      });

      setTimeout(() => this.setState({ fading: false }), 500);
    });
  }

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
    return this.state.studies.map((s, i) => {
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
                key={i}
                id={id}
                opts={this.state.roles.map((r) => {
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
                key={i}
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
    const rolesSelected = this.state.rolesSelected.filter(
      (x) => x.study != studyId
    );
    rolesSelected.push({ study: studyId, role: roleId });
    this.setState({ rolesSelected });
  };

  getSelectedRole = (id: number) => {
    const { rolesSelected } = this.state;
    if (rolesSelected.some((x) => x.study == id)) {
      return rolesSelected.filter((x) => x.study == id)[0].role;
    } else {
      return 0;
    }
  };

  isActiveAccessGroup = (id: number): boolean => {
    return this.state.accessGroupsSelected.some((ag) => ag.id == id);
  };

  addAccessGroup = (id: number, callback: () => void): void => {
    const { accessGroups, accessGroupsSelected } = this.state;
    const accessGroup = accessGroups.filter((ag) => ag.id == id)[0];

    if (accessGroup) {
      accessGroupsSelected.push(accessGroup);
      this.setState({ accessGroupsSelected }, callback);
    }
  };

  removeAccessGroup = (id: number, callback: () => void): void => {
    const accessGroupsSelected = this.state.accessGroupsSelected.filter(
      (ag) => ag.id != id
    );
    this.setState({ accessGroupsSelected }, callback);
  };

  isActiveStudy = (id: number): boolean => {
    return this.state.studiesSelected.some((s) => s.id == id);
  };

  addStudy = (id: number, callback: () => void): void => {
    const { studies, studiesSelected } = this.state;
    const study = Object.assign({}, studies.filter((s) => s.id == id)[0]);

    if (study) {
      studiesSelected.push(study);
      this.setState({ studiesSelected }, callback);
    }
  };

  removeStudy = (id: number, callback: () => void): void => {
    const studiesSelected = this.state.studiesSelected.filter(
      (s) => s.id != id
    );
    this.setState({ studiesSelected }, callback);
  };

  create = (): void => {
    const { email, firstName, lastName } = this.state;
    const body = {
      app: 1,
      create: {
        email: email,
        first_name: firstName,
        last_name: lastName
      }
    };

    const opts = {
      method: "POST",
      body: JSON.stringify(body)
    };

    makeRequest("/admin/account/create", opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    console.log(res.msg);
  };

  handleFailure = (res: ResponseBody) => {
    console.log(res.msg);
  };

  getAccessGroupsSummary = () => {
    return this.state.accessGroupsSelected.map((ag, i) => {
      const permissions = ag.permissions.map((p, i) => {
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
    const { roles, rolesSelected, studiesSelected } = this.state;

    return studiesSelected.map((s, i) => {
      let role;
      let permissions;
      const selectedRole = rolesSelected.filter((sr) => sr.study == s.id)[0];

      if (selectedRole) {
        role = roles.filter((r) => r.id == selectedRole.role)[0];

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
              {" " + role.name}
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
      fading,
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
                  <div className="loader-container">
                    {loading || fading ? (
                      <SmallLoader loading={loading} />
                    ) : null}
                    {loading ? null : (
                      <Table
                        columns={columnsAccessGroups}
                        control={<React.Fragment />}
                        controlWidth={0}
                        data={this.getAccessGroupsData()}
                        includeControl={false}
                        includeSearch={false}
                        paginationPer={2}
                        sortDefault="Name"
                      />
                    )}
                  </div>
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <span>Assign Account to Studies</span>
                  <div className="loader-container">
                    {loading || fading ? (
                      <SmallLoader loading={loading} />
                    ) : null}
                    {loading ? null : (
                      <Table
                        columns={columnsStudies}
                        control={<React.Fragment />}
                        controlWidth={0}
                        data={this.getStudiesData()}
                        includeControl={false}
                        includeSearch={false}
                        paginationPer={2}
                        sortDefault="Name"
                      />
                    )}
                  </div>
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
          <button className="button-primary" onClick={this.create}>
            Create
          </button>
        </div>
      </div>
    );
  }
}

export default AccountsEdit;
