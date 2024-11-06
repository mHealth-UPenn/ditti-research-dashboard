import * as React from "react";
import { Component } from "react";
import { ViewProps } from "../../interfaces";
import TextField from "../fields/textField";

interface AppsEditProps extends ViewProps {
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
                    type="text"
                    placeholder=""
                    value={name}
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
