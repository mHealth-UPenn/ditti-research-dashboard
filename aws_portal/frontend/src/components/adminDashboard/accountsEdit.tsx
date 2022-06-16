import * as React from "react";
import { Component } from "react";
import Table, { Column } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";

interface AccessGroup {
  id: number;
  name: string;
  app: string;
  permissions: {
    id: number;
    action: string;
    resource: string;
  }[];
}

const accessGroupsRaw: AccessGroup[] = [
  {
    id: 0,
    name: "DittiApp Staff",
    app: "DittiApp Dashboard",
    permissions: [
      {
        id: 0,
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
        id: 0,
        action: "View",
        resource: "Admin Dashboard"
      }
    ]
  }
];

const studies = [
  {
    id: 0,
    name: "MSBI",
    accessGroup: "DittiApp Staff",
    roles: [
      {
        id: 0,
        name: "Admin",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
            action: "View",
            resource: "Taps"
          },
          {
            id: 0,
            action: "Add",
            resource: "Users"
          },
          {
            id: 0,
            action: "Edit",
            resource: "Users"
          },
          {
            id: 0,
            action: "Delete",
            resource: "Users"
          }
        ]
      },
      {
        id: 0,
        name: "Coordinator",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
            action: "View",
            resource: "Taps"
          },
          {
            id: 0,
            action: "Add",
            resource: "Users"
          }
        ]
      },
      {
        id: 0,
        name: "Viewer",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
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
    accessGroup: "DittiApp Staff",
    roles: [
      {
        id: 0,
        name: "Admin",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
            action: "View",
            resource: "Taps"
          },
          {
            id: 0,
            action: "Add",
            resource: "Users"
          },
          {
            id: 0,
            action: "Edit",
            resource: "Users"
          },
          {
            id: 0,
            action: "Delete",
            resource: "Users"
          }
        ]
      },
      {
        id: 0,
        name: "Coordinator",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
            action: "View",
            resource: "Taps"
          },
          {
            id: 0,
            action: "Add",
            resource: "Users"
          }
        ]
      },
      {
        id: 0,
        name: "Viewer",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
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
    accessGroup: "DittiApp Staff",
    roles: [
      {
        id: 0,
        name: "Admin",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
            action: "View",
            resource: "Taps"
          },
          {
            id: 0,
            action: "Add",
            resource: "Users"
          },
          {
            id: 0,
            action: "Edit",
            resource: "Users"
          },
          {
            id: 0,
            action: "Delete",
            resource: "Users"
          }
        ]
      },
      {
        id: 0,
        name: "Coordinator",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
            action: "View",
            resource: "Taps"
          },
          {
            id: 0,
            action: "Add",
            resource: "Users"
          }
        ]
      },
      {
        id: 0,
        name: "Viewer",
        permissions: [
          {
            id: 0,
            action: "View",
            resource: "Users"
          },
          {
            id: 0,
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
  firstName: string;
  lastName: string;
  email: string;
  accessGroups: AccessGroup[];
  studies: {
    id: number;
    name: string;
    accessGroup: string;
    roles: {
      id: number;
      name: string;
      permissions: {
        id: number;
        action: string;
        resource: string;
      }[];
    }[];
  }[];
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
          firstName: "",
          lastName: "",
          email: "",
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
          sortable: true,
          searchable: false,
          width: 10
        }
      ],
      firstName: prefill.firstName,
      lastName: prefill.lastName,
      email: prefill.email,
      accessGroups: prefill.accessGroups,
      studies: prefill.studies
    };
  }

  getPrefill(id: number) {
    return {
      firstName: "",
      lastName: "",
      email: "",
      accessGroups: [],
      studies: []
    };
  }

  getAccessGroupsData() {
    return accessGroupsRaw.map((accessGroup) => {
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
                add={(id: number, callback: (ids: number[]) => void) =>
                  this.addAccessGroup(id, callback)
                }
                ids={this.state.accessGroups.map((x) => x.id)}
                id={id}
                remove={(id: number, callback: (ids: number[]) => void) =>
                  this.removeAccessGroup(id, callback)
                }
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
    return studies.map((study) => {
      const { name, accessGroup } = study;

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
            <div className="flex-left table-data">
              <span>Select role...</span>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        },
        {
          contents: (
            <div className="flex-left table-control">
              <button className="button-secondary" onClick={() => null}>
                Add&nbsp;+
              </button>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  }

  addAccessGroup(id: number, callback: (ids: number[]) => void): void {
    const { accessGroups } = this.state;
    const accessGroup = accessGroupsRaw.filter((x) => x.id == id).pop();

    if (accessGroup) {
      accessGroups.push(accessGroup);
      const ids = accessGroups.map((x: AccessGroup) => x.id);
      this.setState({ accessGroups }, () => callback(ids));
    }
  }

  removeAccessGroup(id: number, callback: (ids: number[]) => void): void {
    const accessGroups = this.state.accessGroups.filter((x) => x.id != id);
    const ids = accessGroups.map((x: AccessGroup) => x.id);
    this.setState({ accessGroups }, () => callback(ids));
  }

  render() {
    const { accountId } = this.props;
    const {
      accessGroups,
      columnsAccessGroups,
      columnsStudies,
      firstName,
      lastName,
      email
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
            {accessGroups.map((accessGroup, i) => {
              const permissions = accessGroup.permissions.map(
                (permission, i) => {
                  return (
                    <span key={i}>
                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                      {permission.action + " - " + permission.resource}
                      <br />
                    </span>
                  );
                }
              );

              return (
                <span key={i}>
                  {i ? <br /> : ""}
                  &nbsp;&nbsp;&nbsp;&nbsp;{accessGroup.name}
                  <br />
                  &nbsp;&nbsp;&nbsp;&nbsp;Permissions:
                  <br />
                  {permissions}
                </span>
              );
            })}
            <br />
            Studies:
            <br />
          </span>
          <button className="button-primary">Create</button>
        </div>
      </div>
    );
  }
}

export default AccountsEdit;
