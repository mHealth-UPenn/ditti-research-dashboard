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
  name: string;
  acronym: string;
  dittiId: string;
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
          dittiId: ""
        };

    this.state = {
      name: prefill.name,
      acronym: prefill.acronym,
      dittiId: prefill.dittiId
    };
  }

  getPrefill(id: number) {
    return {
      name: "",
      acronym: "",
      dittiId: ""
    };
  }

  create = (): void => {
    const { acronym, dittiId, name } = this.state;

    const body = {
      app: 1,
      create: {
        acronym: acronym,
        ditti_id: dittiId,
        name: name
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

  render() {
    const { studyId } = this.props;
    const { name, acronym, dittiId } = this.state;

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
