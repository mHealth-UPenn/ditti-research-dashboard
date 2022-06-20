import * as React from "react";
import { Component } from "react";
import Table, { Column } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";
import { studiesRaw } from "./accountsEdit";
import Select from "../fields/select";
import { App, Study } from "../interfaces";

const appsRaw: App[] = [
  {
    id: 1,
    name: "Ditti App Dashboard"
  },
  {
    id: 2,
    name: "Admin Dashboard"
  }
];

interface AccessGroupsEditProps {
  accessGroupId: number;
}

interface AccessGroupsEditState {
  columnsStudies: Column[];
  name: string;
  app: App;
  studies: Study[];
}

class AccessGroupsEdit extends React.Component<
  AccessGroupsEditProps,
  AccessGroupsEditState
> {
  constructor(props: AccessGroupsEditProps) {
    super(props);

    const { accessGroupId } = props;
    const prefill = accessGroupId
      ? this.getPrefill(accessGroupId)
      : {
          name: "",
          app: {} as App,
          studies: []
        };

    this.state = {
      columnsStudies: [
        {
          name: "Name",
          sortable: true,
          searchable: false,
          width: 65
        },
        {
          name: "Acronym",
          sortable: true,
          searchable: false,
          width: 25
        },
        {
          name: "",
          sortable: false,
          searchable: false,
          width: 10
        }
      ],
      name: prefill.name,
      app: prefill.app,
      studies: prefill.studies
    };
  }

  getPrefill(id: number) {
    return {
      name: "",
      app: {} as App,
      studies: []
    };
  }

  getStudiesData() {
    return studiesRaw.map((study, i) => {
      const { id, name, acronym } = study;

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
              <span>{acronym}</span>
            </div>
          ),
          searchValue: "",
          sortValue: acronym
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

  isActiveStudy = (id: number): boolean => {
    return this.state.studies.some((s) => s.id == id);
  };

  addStudy = (id: number, callback: () => void): void => {
    const { studies } = this.state;
    const study = studiesRaw.filter((s) => s.id == id)[0];

    if (study) {
      studies.push(study);
      this.setState({ studies }, callback);
    }
  };

  removeStudy = (id: number, callback: () => void): void => {
    const studies = this.state.studies.filter((r) => r.id != id);
    this.setState({ studies }, callback);
  };

  getStudiesSummary = () => {
    return this.state.studies.map((study, i) => (
      <span key={i}>
        {study.name}
        <br />
      </span>
    ));
  };

  selectApp = (id: number): void => {
    const app = appsRaw.filter((a) => a.id == id)[0];
    if (app) this.setState({ app });
  };

  getSelectedApp = (): number => {
    const { app } = this.state;
    return app ? app.id : 0;
  };

  render() {
    const { accessGroupId } = this.props;
    const { columnsStudies, name, app } = this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {accessGroupId ? "Edit " : "Create "} Access Group
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
                  <div style={{ marginBottom: "0.5rem" }}>
                    <b>App</b>
                  </div>
                  <div className="border-light">
                    <Select
                      id={accessGroupId}
                      opts={appsRaw.map((a) => {
                        return { value: a.id, label: a.name };
                      })}
                      placeholder="Select app..."
                      callback={this.selectApp}
                      getDefault={this.getSelectedApp}
                    />
                  </div>
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <span>Add Studies to Access Group</span>
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
          <h1 className="border-white-b">Access Group Summary</h1>
          <span>
            Name: {name}
            <br />
            App: {app.name}
            <br />
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

export default AccessGroupsEdit;
