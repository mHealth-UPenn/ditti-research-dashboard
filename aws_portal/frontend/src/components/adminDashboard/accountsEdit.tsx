import * as React from "react";
import { Component } from "react";
import Table, { Column } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";
import { AccessGroup, Study } from "../../interfaces";
import Select from "../fields/select";

const accessGroupsRaw: AccessGroup[] = [
  {
    id: 10,
    name: "DittiApp Staff",
    app: "DittiApp Dashboard",
    permissions: [
      {
        id: 10,
        action: "View",
        resource: "DittiApp Dashboard"
      }
    ]
  },
  {
    id: 1,
    name: "Admins",
    app: "Admin Dashboard",
    permissions: [
      {
        id: 10,
        action: "View",
        resource: "Admin Dashboard"
      }
    ]
  }
];

export const studiesRaw: Study[] = [
  {
    id: 10,
    name: "MSBI",
    acronym: "MSBI",
    accessGroup: "DittiApp Staff",
    roles: [
      {
        id: 1,
        name: "Admin",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          },
          {
            id: 10,
            action: "Add",
            resource: "Users"
          },
          {
            id: 10,
            action: "Edit",
            resource: "Users"
          },
          {
            id: 10,
            action: "Delete",
            resource: "Users"
          }
        ]
      },
      {
        id: 2,
        name: "Coordinator",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          },
          {
            id: 10,
            action: "Add",
            resource: "Users"
          }
        ]
      },
      {
        id: 3,
        name: "Viewer",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          }
        ]
      }
    ]
  },
  {
    id: 1,
    name: "OSA ART",
    acronym: "OSA",
    accessGroup: "DittiApp Staff",
    roles: [
      {
        id: 1,
        name: "Admin",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          },
          {
            id: 10,
            action: "Add",
            resource: "Users"
          },
          {
            id: 10,
            action: "Edit",
            resource: "Users"
          },
          {
            id: 10,
            action: "Delete",
            resource: "Users"
          }
        ]
      },
      {
        id: 2,
        name: "Coordinator",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          },
          {
            id: 10,
            action: "Add",
            resource: "Users"
          }
        ]
      },
      {
        id: 3,
        name: "Viewer",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          }
        ]
      }
    ]
  },
  {
    id: 2,
    name: "Caregiver ART",
    acronym: "Caregiver",
    accessGroup: "DittiApp Staff",
    roles: [
      {
        id: 1,
        name: "Admin",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          },
          {
            id: 10,
            action: "Add",
            resource: "Users"
          },
          {
            id: 10,
            action: "Edit",
            resource: "Users"
          },
          {
            id: 10,
            action: "Delete",
            resource: "Users"
          }
        ]
      },
      {
        id: 2,
        name: "Coordinator",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          },
          {
            id: 10,
            action: "Add",
            resource: "Users"
          }
        ]
      },
      {
        id: 2,
        name: "Viewer",
        permissions: [
          {
            id: 10,
            action: "View",
            resource: "Users"
          },
          {
            id: 10,
            action: "View",
            resource: "Taps"
          }
        ]
      }
    ]
  }
];

interface AccountsEditProps {
  accountId: number;
}

interface AccountsEditState {
  columnsAccessGroups: Column[];
  columnsStudies: Column[];
  selectedRoles: { study: number; role: number }[];
  email: string;
  firstName: string;
  lastName: string;
  accessGroups: AccessGroup[];
  studies: Study[];
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
          selectedRoles: [],
          email: "",
          firstName: "",
          lastName: "",
          accessGroups: [],
          studies: []
        };

    this.state = {
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
      firstName: prefill.firstName,
      lastName: prefill.lastName,
      email: prefill.email,
      accessGroups: prefill.accessGroups,
      selectedRoles: prefill.selectedRoles,
      studies: prefill.studies
    };
  }

  getPrefill(id: number) {
    return {
      firstName: "",
      lastName: "",
      email: "",
      accessGroups: [],
      selectedRoles: [],
      studies: []
    };
  }

  getAccessGroupsData() {
    return accessGroupsRaw.map((accessGroup, i) => {
      const { id, name, app } = accessGroup;

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
              <span>{app}</span>
            </div>
          ),
          searchValue: "",
          sortValue: app
        },
        {
          contents: (
            <div className="flex-left table-control">
              <ToggleButton
                key={i}
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
  }

  getStudiesData() {
    return studiesRaw.map((study, i) => {
      const { accessGroup, id, name, roles } = study;

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
              <span>{accessGroup}</span>
            </div>
          ),
          searchValue: "",
          sortValue: accessGroup
        },
        {
          contents: (
            <div className="flex-left" style={{ position: "relative" }}>
              <Select
                key={i}
                id={study.id}
                opts={study.roles.map((r) => {
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
  }

  getSelectedRole = (id: number) => {
    const { selectedRoles } = this.state;
    if (selectedRoles.some((x) => x.study == id)) {
      return selectedRoles.filter((x) => x.study == id)[0].role;
    } else {
      return 0;
    }
  };

  isActiveAccessGroup = (id: number): boolean => {
    return this.state.accessGroups.some((ag) => ag.id == id);
  };

  addAccessGroup = (id: number, callback: () => void): void => {
    const { accessGroups } = this.state;
    const accessGroup = accessGroupsRaw.filter((ag) => ag.id == id)[0];

    if (accessGroup) {
      accessGroups.push(accessGroup);
      this.setState({ accessGroups }, callback);
    }
  };

  removeAccessGroup = (id: number, callback: () => void): void => {
    const accessGroups = this.state.accessGroups.filter((ag) => ag.id != id);
    this.setState({ accessGroups }, callback);
  };

  isActiveStudy = (id: number): boolean => {
    return this.state.studies.some((s) => s.id == id);
  };

  addStudy = (id: number, callback: () => void): void => {
    const { studies } = this.state;
    const study = Object.assign({}, studiesRaw.filter((s) => s.id == id)[0]);

    if (study) {
      studies.push(study);
      this.setState({ studies }, callback);
    }
  };

  removeStudy = (id: number, callback: () => void): void => {
    const studies = this.state.studies.filter((s) => s.id != id);
    this.setState({ studies }, callback);
  };

  selectRole = (roleId: number, studyId: number): void => {
    const selectedRoles = this.state.selectedRoles.filter(
      (x) => x.study != studyId
    );
    selectedRoles.push({ study: studyId, role: roleId });
    this.setState({ selectedRoles });
  };

  getAccessGroupsSummary = () => {
    return this.state.accessGroups.map((accessGroup, i) => {
      const permissions = accessGroup.permissions.map((permission, i) => {
        return (
          <span key={i}>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            {permission.action + " - " + permission.resource}
            <br />
          </span>
        );
      });

      return (
        <span key={i}>
          {i ? <br /> : ""}
          &nbsp;&nbsp;&nbsp;&nbsp;
          {accessGroup.name}
          <br />
          &nbsp;&nbsp;&nbsp;&nbsp;Permissions:
          <br />
          {permissions}
        </span>
      );
    });
  };

  getStudiesSummary = () => {
    const { selectedRoles, studies } = this.state;

    return studies.map((study, i) => {
      let role;
      let permissions;
      const selectedRole = selectedRoles.filter(
        (sr) => sr.study == study.id
      )[0];

      if (selectedRole) {
        role = study.roles.filter((r) => r.id == selectedRole.role)[0];

        if (role) {
          permissions = role.permissions.map((permission, j) => {
            return (
              <span key={j}>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                {permission.action + " - " + permission.resource}
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
          {study.name}
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
    const { columnsAccessGroups, columnsStudies, email, firstName, lastName } =
      this.state;

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
                    paginationPer={2}
                    sortDefault="Name"
                  />
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
          <button className="button-primary">Create</button>
        </div>
      </div>
    );
  }
}

export default AccountsEdit;
