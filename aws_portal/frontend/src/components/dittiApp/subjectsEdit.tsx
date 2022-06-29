import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import { ResponseBody, User, UserDetails, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import CheckField from "../fields/checkField";
import { SmallLoader } from "../loader";

interface SubjectsEditProps extends ViewProps {
  dittiId: string;
  studyId: number;
  studyPrefix: string;
  studyEmail: string;
}

interface SubjectsEditState extends UserDetails {
  loading: boolean;
}

class SubjectsEdit extends React.Component<
  SubjectsEditProps,
  SubjectsEditState
> {
  state = {
    tap_permission: false,
    information: "",
    user_permission_id: "",
    exp_time: "",
    team_email: "",
    loading: true
  };

  componentDidMount() {
    this.getPrefill().then((prefill: UserDetails) =>
      this.setState({ ...prefill, loading: false })
    );
  }

  getPrefill = async (): Promise<UserDetails> => {
    const id = this.props.dittiId;
    return id
      ? makeRequest(
          `/aws/scan?app=2&key=User&query=user_permission_id=="${id}"`
        ).then(this.makePrefill)
      : {
          tap_permission: false,
          information: "",
          user_permission_id: "",
          exp_time: "",
          team_email: ""
        };
  };

  makePrefill = (res: User[]): UserDetails => {
    const user = res[0];

    return {
      tap_permission: user.tap_permission,
      information: user.information,
      user_permission_id: user.user_permission_id,
      exp_time: user.exp_time,
      team_email: user.team_email
    };
  };

  post = (): void => {
    const {
      tap_permission,
      information,
      user_permission_id,
      exp_time,
      team_email
    } = this.state;

    const data = {
      tap_permission,
      information,
      user_permission_id,
      exp_time,
      team_email
    };

    const id = this.props.dittiId;
    const body = {
      app: 2,
      study: this.props.studyId,
      ...(id ? { user_permission_id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/aws/user/edit" : "/aws/user/create";

    makeRequest(url, opts).then(this.handleSuccess).catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    const { goBack, flashMessage } = this.props;

    goBack();
    flashMessage(<span>{res.msg}</span>, "success");
  };

  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    const msg = (
      <span>
        <b>An unexpected error occured:</b>
        <br />
        {res.msg}
      </span>
    );

    flashMessage(msg, "danger");
  };

  render() {
    const { dittiId, studyEmail, studyPrefix } = this.props;
    const {
      tap_permission,
      information,
      user_permission_id,
      exp_time,
      loading
    } = this.state;

    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    };

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          {loading ? (
            <SmallLoader />
          ) : (
            <div className="admin-form">
              <div className="admin-form-content">
                <h1 className="border-light-b">
                  {dittiId ? "Edit " : "Enroll "} Subject
                </h1>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="dittiId"
                      type="text"
                      placeholder=""
                      prefill={user_permission_id.replace(studyPrefix, "")}
                      label="Ditti ID"
                      onKeyup={(text: string) => {
                        const user_permission_id = studyPrefix + text;
                        this.setState({ user_permission_id });
                      }}
                      feedback=""
                    >
                      <div className="disabled bg-light border-light-r">
                        <span>
                          <i>{studyPrefix}</i>
                        </span>
                      </div>
                    </TextField>
                  </div>
                  <div className="admin-form-field">
                    <TextField
                      label="Team Email"
                      prefill={studyEmail}
                      disabled={true}
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="expiresOn"
                      type="datetime-local"
                      placeholder=""
                      prefill={exp_time.replace("Z", "")}
                      label="Expires On"
                      onKeyup={(text: string) =>
                        this.setState({ exp_time: text + ":00.000Z" })
                      }
                      feedback=""
                    />
                  </div>
                  <div className="admin-form-field">
                    <CheckField
                      id="tapping-access"
                      prefill={tap_permission}
                      label="Tapping Access"
                      onChange={(val) => this.setState({ tap_permission: val })}
                    />
                  </div>
                </div>
                <div className="admin-form-row">
                  <div className="admin-form-field">
                    <TextField
                      id="information"
                      type="text"
                      placeholder=""
                      prefill={information}
                      label="About sleep template (optional)"
                      onKeyup={() => null}
                      feedback=""
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Study Summary</h1>
          <span>
            Ditti ID:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{user_permission_id}
            <br />
            <br />
            Team email:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{studyEmail}
            <br />
            <br />
            Expires on:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;
            {exp_time
              ? new Date(exp_time).toLocaleDateString("en-US", dateOptions)
              : ""}
            <br />
            <br />
            Tapping access:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{tap_permission ? "Yes" : "No"}
            <br />
            <br />
            About sleep template:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;None
            <br />
          </span>
          {dittiId ? (
            <button className="button-primary" onClick={this.post}>
              Update
            </button>
          ) : (
            <button className="button-primary" onClick={this.post}>
              Enroll
            </button>
          )}
          <div style={{ marginTop: "1.5rem" }}>
            <i>
              After enrolling a subject, log in on your smartphone using their
              Ditti ID to ensure their account was created successfully.
            </i>
          </div>
        </div>
      </div>
    );
  }
}

export default SubjectsEdit;
