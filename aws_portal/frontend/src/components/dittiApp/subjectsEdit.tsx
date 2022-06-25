import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import { ResponseBody, User, UserDetails } from "../../interfaces";
import { makeRequest } from "../../utils";

interface SubjectsEditProps {
  dittiId: string;
  studyId: number;
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
      app: "DittiApp",
      study: this.props.studyId,
      ...(id ? { user_permission_id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/aws/user/edit" : "/aws/user/create";
    makeRequest(url, opts).then(this.handleSuccess).catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    console.log(res.msg);
  };

  handleFailure = (res: ResponseBody) => {
    console.log(res.msg);
  };

  render() {
    const { dittiId } = this.props;
    const {
      tap_permission,
      information,
      user_permission_id,
      exp_time,
      team_email
    } = this.state;

    return (
      <div className="page-container" style={{ flexDirection: "row" }}>
        <div className="page-content bg-white">
          <div className="admin-form">
            <div className="admin-form-content">
              <h1 className="border-light-b">
                {dittiId ? "Edit " : "Enroll "} Subject
              </h1>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="dittiId"
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={user_permission_id}
                    label="Ditti ID"
                    onKeyup={(text: string) =>
                      this.setState({ user_permission_id: text })
                    }
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">
                  <TextField
                    id="email"
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={team_email}
                    label="Team email"
                    onKeyup={() => null}
                    feedback=""
                  />
                </div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="expiresOn"
                    svg={<React.Fragment />}
                    type="text"
                    placeholder=""
                    prefill={exp_time}
                    label="Expires On"
                    onKeyup={() => null}
                    feedback=""
                  />
                </div>
                <div className="admin-form-field">Tapping Access</div>
              </div>
              <div className="admin-form-row">
                <div className="admin-form-field">
                  <TextField
                    id="information"
                    svg={<React.Fragment />}
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
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Study Summary</h1>
          <span>
            Ditti ID: {user_permission_id}
            <br />
            <br />
            Team email:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{team_email}
            <br />
            <br />
            Expires on:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{exp_time}
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
