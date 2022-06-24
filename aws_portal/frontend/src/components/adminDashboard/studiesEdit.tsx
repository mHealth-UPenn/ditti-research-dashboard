import * as React from "react";
import { Component } from "react";
import Table, { Column, TableData } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";
import { ResponseBody, Role } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";

interface StudiesEditProps {
  studyId: number;
}

interface StudiesEditState {
  roles: Role[];
  columnsRoles: Column[];
  loading: boolean;
  fading: boolean;
  name: string;
  acronym: string;
  dittiId: string;
  rolesSelected: Role[];
}

class StudiesEdit extends React.Component<StudiesEditProps, StudiesEditState> {
  constructor(props: StudiesEditProps) {
    super(props);

    const { studyId } = props;
    const prefill = studyId
      ? this.getPrefill(studyId)
      : {
          name: "",
          acronym: "",
          dittiId: "",
          rolesSelected: []
        };

    this.state = {
      roles: [],
      columnsRoles: [
        {
          name: "Name",
          sortable: true,
          searchable: false,
          width: 25
        },
        {
          name: "Permissions",
          sortable: false,
          searchable: false,
          width: 65
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
      name: prefill.name,
      acronym: prefill.acronym,
      dittiId: prefill.dittiId,
      rolesSelected: prefill.rolesSelected
    };
  }

  getPrefill(id: number) {
    return {
      name: "",
      acronym: "",
      dittiId: "",
      rolesSelected: []
    };
  }

  componentDidMount() {
    makeRequest("/admin/role?app=1").then((roles) => {
      this.setState({ roles, loading: false, fading: true });
      setTimeout(() => this.setState({ fading: false }), 500);
    });
  }

  getRolesData = (): TableData[][] => {
    return this.state.roles.map((role: Role) => {
      const { id, name, permissions } = role;

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
              <span>
                {permissions
                  .map((p) => p.action + " - " + p.resource)
                  .join(", ")}
              </span>
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
                getActive={this.isActiveRole}
                add={this.addRole}
                remove={this.removeRole}
              />
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  isActiveRole = (id: number): boolean => {
    return this.state.rolesSelected.some((r) => r.id == id);
  };

  addRole = (id: number, callback: () => void): void => {
    const { rolesSelected } = this.state;
    const role = this.state.roles.filter((r) => r.id == id)[0];

    if (role) {
      rolesSelected.push(role);
      this.setState({ rolesSelected }, callback);
    }
  };

  removeRole = (id: number, callback: () => void): void => {
    const rolesSelected = this.state.rolesSelected.filter((r) => r.id != id);
    this.setState({ rolesSelected }, callback);
  };

  create = (): void => {
    const { acronym, dittiId, name, rolesSelected } = this.state;

    const roles = rolesSelected.map((r) => {
      return { id: r.id };
    });

    const body = {
      app: 1,
      create: {
        acronym: acronym,
        ditti_id: dittiId,
        name: name,
        roles: roles
      }
    };

    const opts = {
      method: "POST",
      body: JSON.stringify(body)
    };

    makeRequest("/admin/study/create", opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    console.log(res.msg);
  };

  handleFailure = (res: ResponseBody) => {
    console.log(res.msg);
  };

  getRolesSummary = () => {
    const { rolesSelected } = this.state;

    return rolesSelected.map((role, i) => {
      const permissions = role.permissions.map((permission, j) => {
        return (
          <span key={j}>
            &nbsp;&nbsp;&nbsp;&nbsp;
            {permission.action + " - " + permission.resource}
            <br />
          </span>
        );
      });

      return (
        <span key={i}>
          {i ? <br /> : ""}
          {role.name}
          <br />
          {permissions}
        </span>
      );
    });
  };

  render() {
    const { studyId } = this.props;
    const { columnsRoles, loading, fading, name, acronym, dittiId } =
      this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {studyId ? "Edit " : "Create "} Study
              </h1>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="name"
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={name}
                    label="Name"
                    onKeyup={(text: string) => this.setState({ name: text })}
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="acronym"
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={acronym}
                    label="Acronym"
                    onKeyup={(text: string) => this.setState({ acronym: text })}
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <TextField
                    id="dittiId"
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={dittiId}
                    label="Ditti ID"
                    onKeyup={(text: string) => this.setState({ dittiId: text })}
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <span>Add Roles to Study</span>
                  <div className="loader-container">
                    {loading || fading ? (
                      <SmallLoader loading={loading} />
                    ) : null}
                    {loading ? null : (
                      <Table
                        columns={columnsRoles}
                        control={<React.Fragment />}
                        controlWidth={0}
                        data={this.getRolesData()}
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
          <h1 className="border-white-b">Study Summary</h1>
          <span>
            Name: {name}
            <br />
            Acronym: {acronym}
            <br />
            Ditti ID: {dittiId}
            <br />
            <br />
            Roles:
            <br />
            {this.getRolesSummary()}
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

export default StudiesEdit;
