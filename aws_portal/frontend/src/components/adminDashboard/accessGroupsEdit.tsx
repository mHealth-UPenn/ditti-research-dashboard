import * as React from "react";
import { Component } from "react";
import Table, { Column, TableData } from "../table/table";
import TextField from "../fields/textField";
import ToggleButton from "../buttons/toggleButton";
import Select from "../fields/select";
import { App, Study } from "../../interfaces";
import { makeRequest } from "../../utils";

// const appsRaw: App[] = [
//   {
//     id: 1,
//     name: "Ditti App Dashboard"
//   },
//   {
//     id: 2,
//     name: "Admin Dashboard"
//   }
// ];

interface AccessGroupsEditProps {
  accessGroupId: number;
}

interface AccessGroupsEditState {
  apps: App[];
  studies: Study[];
  columnsStudies: Column[];
  name: string;
  appSelected: App;
  studiesSelected: Study[];
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
          studiesSelected: []
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
      apps: [],
      appSelected: prefill.app,
      studies: [],
      studiesSelected: prefill.studiesSelected
    };
  }

  async componentDidMount() {
    const apps: App[] = await makeRequest("/admin/app?app=1");
    const studies: Study[] = await makeRequest("/admin/study?app=1");
    this.setState({ apps, studies });
  }

  getPrefill(id: number) {
    return {
      name: "",
      app: {} as App,
      studiesSelected: []
    };
  }

  getStudiesData = (): TableData[][] => {
    return this.state.studies.map((s: Study) => {
      const { id, name, acronym } = s;

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

  isActiveStudy = (id: number): boolean => {
    return this.state.studiesSelected.some((s) => s.id == id);
  };

  addStudy = (id: number, callback: () => void): void => {
    const { studies, studiesSelected } = this.state;
    const study = studies.filter((s) => s.id == id)[0];

    if (study) {
      studiesSelected.push(study);
      this.setState({ studiesSelected }, callback);
    }
  };

  removeStudy = (id: number, callback: () => void): void => {
    const studiesSelected = this.state.studiesSelected.filter(
      (r) => r.id != id
    );
    this.setState({ studiesSelected }, callback);
  };

  getStudiesSummary = () => {
    return this.state.studiesSelected.map((s, i) => (
      <span key={i}>
        {s.name}
        <br />
      </span>
    ));
  };

  selectApp = (id: number): void => {
    const appSelected = this.state.apps.filter((a) => a.id == id)[0];
    if (appSelected) this.setState({ appSelected });
  };

  getSelectedApp = (): number => {
    const { appSelected } = this.state;
    return appSelected ? appSelected.id : 0;
  };

  render() {
    const { accessGroupId } = this.props;
    const { columnsStudies, name, apps, appSelected } = this.state;

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
                      opts={apps.map((a) => {
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
            App: {appSelected.name}
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
