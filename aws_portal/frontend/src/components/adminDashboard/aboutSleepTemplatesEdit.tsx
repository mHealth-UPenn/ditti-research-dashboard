import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import {
  AboutSleepTemplate,
  ResponseBody,
  Study,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

/**
 * The form's prefill
 */
interface AboutSleepTemplatePrefill {
  name: string;
  text: string;
}

/**
 * aboutSleepTemplateId: the database primary key, 0 if creating a new entry
 */
interface AboutSleepTempaltesEditProps extends ViewProps {
  aboutSleepTemplateId: number;
}

/**
 * loading: whether to show the loader
 */
interface AboutSleepTempaltesEditState extends AboutSleepTemplatePrefill {
  loading: boolean;
}

class AboutSleepTempaltesEdit extends React.Component<
  AboutSleepTempaltesEditProps,
  AboutSleepTempaltesEditState
> {
  state = {
    name: "",
    text: "",
    loading: true
  };

  componentDidMount() {

    // set any form prefill data and hide the loader
    this.getPrefill().then((prefill: AboutSleepTemplatePrefill) =>
      this.setState({ ...prefill, loading: false })
    );
  }

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  getPrefill = async (): Promise<AboutSleepTemplatePrefill> => {
    const id = this.props.aboutSleepTemplateId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/about-sleep-template?app=1&id=" + id).then(
          this.makePrefill
        )
      : {
          name: "",
          text: ""
        };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  makePrefill = (res: AboutSleepTemplate[]): AboutSleepTemplatePrefill => {
    const aboutSleepTemplate = res[0];

    return {
      name: aboutSleepTemplate.name,
      text: aboutSleepTemplate.text
    };
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  post = async (): Promise<void> => {
    const { text, name } = this.state;
    const data = { text, name };
    const id = this.props.aboutSleepTemplateId;
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id
      ? "/admin/about-sleep-template/edit"
      : "/admin/about-sleep-template/create";

    await makeRequest(url, opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  handleSuccess = (res: ResponseBody) => {
    const { goBack, flashMessage } = this.props;

    // go back to the list view and flash a message
    goBack();
    flashMessage(<span>{res.msg}</span>, "success");
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    // flash the message from the backend or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  render() {
    const { aboutSleepTemplateId } = this.props;
    const { name, text, loading } = this.state;
    const buttonText = aboutSleepTemplateId ? "Update" : "Create";

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>

        {/* the edit/create form */}
        <div className="page-content bg-white">
          {loading ? (
            <SmallLoader />
          ) : (
            <div className="admin-form">
              <div className="admin-form-content">
                <h1 className="border-light-b">
                  {aboutSleepTemplateId ? "Edit " : "Create "} Template
                </h1>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="name"
                      prefill={name}
                      label="Name"
                      onKeyup={(text: string) => this.setState({ name: text })}
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="text"
                      type="textarea"
                      prefill={text}
                      label="Text"
                      onKeyup={(text: string) => this.setState({ text: text })}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* the edit/create summary */}
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Template Summary</h1>
          <span>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br />
          </span>
          <AsyncButton onClick={this.post} text={buttonText} type="primary" />
          <div style={{ marginTop: "1.5rem" }}>
            <i>
              To preview this template, you must update an existing user or
              create a new user with this template, then view it through the
              app.
            </i>
          </div>
        </div>
      </div>
    );
  }
}

export default AboutSleepTempaltesEdit;
