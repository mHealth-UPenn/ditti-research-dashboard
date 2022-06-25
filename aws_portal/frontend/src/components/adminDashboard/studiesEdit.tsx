import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import { ResponseBody, Role, Study } from "../../interfaces";
import { makeRequest } from "../../utils";

interface StudiesEditProps {
  studyId: number;
}

interface StudiesEditState {
  name: string;
  acronym: string;
  dittiId: string;
  email: string;
}

class StudiesEdit extends React.Component<StudiesEditProps, StudiesEditState> {
  state = {
    name: "",
    acronym: "",
    dittiId: "",
    email: ""
  };

  componentDidMount() {
    this.getPrefill().then((prefill: StudiesEditState) =>
      this.setState({ ...prefill })
    );
  }

  getPrefill = async (): Promise<StudiesEditState> => {
    const id = this.props.studyId;
    return id
      ? makeRequest("/admin/study?app=1&id=" + id).then(this.makePrefill)
      : {
          name: "",
          acronym: "",
          dittiId: "",
          email: ""
        };
  };

  makePrefill = (res: Study[]): StudiesEditState => {
    const study = res[0];

    return {
      name: study.name,
      acronym: study.acronym,
      dittiId: study.dittiId,
      email: study.email
    };
  };

  post = (): void => {
    const { acronym, dittiId, email, name } = this.state;
    const data = { acronym, ditti_id: dittiId, email, name };
    const id = this.props.studyId;
    console.log(data);
    const body = {
      app: 1,
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/study/edit" : "/admin/study/create";
    makeRequest(url, opts).then(this.handleSuccess).catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    console.log(res.msg);
  };

  handleFailure = (res: ResponseBody) => {
    console.log(res.msg);
  };

  render() {
    const { studyId } = this.props;
    const { name, acronym, dittiId, email } = this.state;

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
                    type="text"
                    placeholder=""
                    prefill={name}
                    label="Name"
                    onKeyup={(text: string) => this.setState({ name: text })}
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <TextField
                    id="email"
                    type="text"
                    placeholder=""
                    prefill={email}
                    label="Team Email"
                    onKeyup={(text: string) => this.setState({ email: text })}
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="acronym"
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
            Team Email: {email}
            <br />
            Acronym: {acronym}
            <br />
            Ditti ID: {dittiId}
            <br />
          </span>
          {studyId ? (
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

export default StudiesEdit;
