import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import { App, ResponseBody } from "../../interfaces";
import { makeRequest } from "../../utils";

interface AppsEditProps {
  appId: number;
}

interface AppsEditState {
  name: string;
}

class AppsEdit extends React.Component<AppsEditProps, AppsEditState> {
  constructor(props: AppsEditProps) {
    super(props);
    const { appId } = props;
    const prefill = appId ? this.getPrefill(appId) : { name: "" };
    this.state = { name: prefill.name };
  }

  getPrefill(id: number) {
    return { name: "" };
  }

  tryCreate = (): void => {
    this.create().then(this.handleCreate, this.handleException);
  };

  create = async (): Promise<ResponseBody> => {
    return fetch("").then((res) => {
      return {
        msg: ""
      };
    });
  };

  handleCreate = (res: ResponseBody): void => {
    console.log(res.msg);
  };

  handleException = (res: ResponseBody): void => {
    console.log(res.msg);
  };

  render() {
    const { appId } = this.props;
    const { name } = this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {appId ? "Edit " : "Create "} App
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
            </div>
          </div>
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">App Summary</h1>
          <span>
            Name: {name}
            <br />
          </span>
          <button className="button-primary">Create</button>
        </div>
      </div>
    );
  }
}

export default AppsEdit;
