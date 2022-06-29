import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import { ResponseBody, User, UserDetails, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import CheckField from "../fields/checkField";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";

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
    tapPermission: false,
    information: "",
    userPermissionId: "",
    expTime: "",
    teamEmail: "",
    createdAt: "",
    loading: true
  };

  componentDidMount() {
    this.getPrefill().then((prefill: UserDetails) => {
      console.log(prefill);
      this.setState({ ...prefill, loading: false });
    });
  }

  getPrefill = async (): Promise<UserDetails> => {
    const id = this.props.dittiId;
    return id
      ? makeRequest(
          `/aws/scan?app=2&key=User&query=user_permission_id=="${id}"`
        ).then(this.makePrefill)
      : {
          tapPermission: false,
          information: "",
          userPermissionId: "",
          expTime: "",
          teamEmail: "",
          createdAt: ""
        };
  };

  makePrefill = (user: User[]): UserDetails => {
    return {
      tapPermission: user[0].tap_permission,
      information: user[0].information,
      userPermissionId: user[0].user_permission_id,
      expTime: user[0].exp_time,
      teamEmail: user[0].team_email,
      createdAt: user[0].createdAt
    };
  };

  post = async (): Promise<void> => {
    const { tapPermission, information, userPermissionId, expTime, teamEmail } =
      this.state;

    const data = {
      tap_permission: tapPermission,
      information: information,
      user_permission_id: userPermissionId,
      exp_time: expTime,
      team_email: teamEmail
    };

    const id = this.props.dittiId;
    const body = {
      app: 2,
      study: this.props.studyId,
      ...(id ? { user_permission_id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/aws/user/edit" : "/aws/user/create";

    await makeRequest(url, opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
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
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  render() {
    const { dittiId, studyEmail, studyPrefix } = this.props;
    const {
      tapPermission,
      information,
      userPermissionId,
      expTime,
      teamEmail,
      loading
    } = this.state;

    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    };

    const buttonText = dittiId ? "Update" : "Create";

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
                      prefill={userPermissionId.replace(studyPrefix, "")}
                      label="Ditti ID"
                      onKeyup={(text: string) => {
                        const user_permission_id = studyPrefix + text;
                        this.setState({ userPermissionId });
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
                      prefill={expTime.replace("Z", "")}
                      label="Expires On"
                      onKeyup={(text: string) =>
                        this.setState({ expTime: text + ":00.000Z" })
                      }
                      feedback=""
                    />
                  </div>
                  <div className="admin-form-field">
                    <CheckField
                      id="tapping-access"
                      prefill={tapPermission}
                      label="Tapping Access"
                      onChange={(val) => this.setState({ tapPermission: val })}
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
            &nbsp;&nbsp;&nbsp;&nbsp;{userPermissionId}
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
            {expTime
              ? new Date(expTime).toLocaleDateString("en-US", dateOptions)
              : ""}
            <br />
            <br />
            Tapping access:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{tapPermission ? "Yes" : "No"}
            <br />
            <br />
            About sleep template:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;None
            <br />
          </span>
          <AsyncButton onClick={this.post} text={buttonText} type="primary" />
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
