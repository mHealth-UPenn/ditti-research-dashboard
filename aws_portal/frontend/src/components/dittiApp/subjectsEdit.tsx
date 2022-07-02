import * as React from "react";
import { Component } from "react";
import TextField from "../fields/textField";
import {
  AboutSleepTemplate,
  ResponseBody,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import "./subjectsEdit.css";
import CheckField from "../fields/checkField";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";
import Select from "../fields/select";

interface SubjectsEditProps extends ViewProps {
  dittiId: string;
  studyId: number;
  studyPrefix: string;
  studyEmail: string;
}

interface SubjectsEditState extends UserDetails {
  aboutSleepTemplates: AboutSleepTemplate[];
  aboutSleepTemplateSelected: AboutSleepTemplate;
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
    aboutSleepTemplates: [],
    aboutSleepTemplateSelected: {} as AboutSleepTemplate,
    loading: true
  };

  componentDidMount() {
    const aboutSleepTemplates = makeRequest(
      "/db/get-about-sleep-templates"
    ).then((aboutSleepTemplates: AboutSleepTemplate[]) =>
      this.setState({ aboutSleepTemplates })
    );

    const prefill = this.getPrefill().then((prefill: UserDetails) =>
      this.setState({ ...prefill })
    );

    Promise.all([aboutSleepTemplates, prefill]).then(() =>
      this.setState({ loading: false })
    );
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
    const aboutSleepTemplateSelected: AboutSleepTemplate =
      this.state.aboutSleepTemplates.filter(
        (ast: AboutSleepTemplate) => ast.text == user[0].information
      )[0];

    if (aboutSleepTemplateSelected)
      this.setState({ aboutSleepTemplateSelected });

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
    const { tapPermission, userPermissionId, expTime, teamEmail } = this.state;

    const data = {
      tap_permission: tapPermission,
      information: this.state.aboutSleepTemplateSelected.text,
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

  selectAboutSleepTemplate = (id: number): void => {
    const aboutSleepTemplateSelected = this.state.aboutSleepTemplates.filter(
      (a: AboutSleepTemplate) => a.id == id
    )[0];

    if (aboutSleepTemplateSelected)
      this.setState({ aboutSleepTemplateSelected });
  };

  getSelectedAboutSleepTemplate = (): number => {
    const { aboutSleepTemplateSelected } = this.state;
    return aboutSleepTemplateSelected ? aboutSleepTemplateSelected.id : 0;
  };

  render() {
    const { dittiId, studyEmail, studyPrefix } = this.props;
    const {
      aboutSleepTemplates,
      aboutSleepTemplateSelected,
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
                        this.setState({ userPermissionId: studyPrefix + text });
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
                    <div style={{ marginBottom: "0.5rem" }}>
                      <b>About Sleep Template</b>
                    </div>
                    <div className="border-light">
                      <Select
                        id={0}
                        opts={aboutSleepTemplates.map(
                          (a: AboutSleepTemplate) => {
                            return { value: a.id, label: a.name };
                          }
                        )}
                        placeholder="Select template..."
                        callback={this.selectAboutSleepTemplate}
                        getDefault={this.getSelectedAboutSleepTemplate}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="admin-form-summary bg-dark">
          <h1 className="border-white-b">Subject Summary</h1>
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
            &nbsp;&nbsp;&nbsp;&nbsp;{aboutSleepTemplateSelected.name}
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
