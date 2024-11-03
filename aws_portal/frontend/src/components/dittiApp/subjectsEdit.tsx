import React, { useState, useEffect } from "react";
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
import FormView from "../containers/forms/formView";
import Form from "../containers/forms/form";
import FormSummary from "../containers/forms/formSummary";
import FormTitle from "../text/formTitle";
import FormRow from "../containers/forms/formRow";
import FormField from "../containers/forms/formField";
import FormSummaryTitle from "../text/formSummaryTitle";
import FormSummaryText from "../containers/forms/formSummaryText";
import FormSummaryButton from "../containers/forms/formSummaryButton";
import FormSummarySubtext from "../containers/forms/formSummarySubtext";
import FormSummaryContent from "../containers/forms/formSummaryContent";

/**
 * dittiId: the subject's ditti id
 * studyId: the study's database primary key
 * studyPrefix: the study's ditti prefix
 * studyEmail: the study's team email
 */
interface SubjectsEditProps extends ViewProps {
  dittiId: string;
  studyId: number;
  studyPrefix: string;
  studyEmail: string;
}

const SubjectsEdit: React.FC<SubjectsEditProps> = ({
  dittiId,
  studyId,
  studyPrefix,
  studyEmail,
  goBack,
  flashMessage,
}) => {
  const [state, setState] = useState<UserDetails>({
    tapPermission: false,
    information: "",
    userPermissionId: "",
    expTime: "",
    teamEmail: "",
    createdAt: ""
  });

  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<AboutSleepTemplate[]>([]);
  const [aboutSleepTemplateSelected, setAboutSleepTemplateSelected] = useState<AboutSleepTemplate>({} as AboutSleepTemplate);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // get all about sleep templates
    const fetchTemplates = makeRequest("/db/get-about-sleep-templates").then(
      (templates: AboutSleepTemplate[]) => setAboutSleepTemplates(templates)
    );

    // get the form's prefill
    const fetchPrefill = getPrefill().then((prefill: UserDetails) =>
      setState(prefill)
    );

    // when all promises finish, hide the loader
    Promise.all([fetchTemplates, fetchPrefill]).then(() =>
      setLoading(false)
    );
  }, [dittiId]);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<UserDetails> => {
    const id = dittiId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest(
          `/aws/scan?app=2&key=User&query=user_permission_id=="${id}"`
        ).then(makePrefill)
      : {
          tapPermission: false,
          information: "",
          userPermissionId: "",
          expTime: "",
          teamEmail: "",
          createdAt: ""
        };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (user: User[]): UserDetails => {
    const selectedTemplate = aboutSleepTemplates.filter(
      (ast: AboutSleepTemplate) => ast.text === user[0].information
    )[0];

    if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);

    return {
      tapPermission: user[0].tap_permission,
      information: user[0].information,
      userPermissionId: user[0].user_permission_id,
      expTime: user[0].exp_time,
      teamEmail: user[0].team_email,
      createdAt: user[0].createdAt
    };
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async (): Promise<void> => {
    const { tapPermission, userPermissionId, expTime, teamEmail } = state;

    const data = {
      tap_permission: tapPermission,
      information: aboutSleepTemplateSelected.text,
      user_permission_id: userPermissionId,
      exp_time: expTime,
      team_email: teamEmail
    };

    const id = dittiId;
    const body = {
      app: 2,  // Ditti Dashboard = 2
      study: studyId,
      ...(id ? { user_permission_id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/aws/user/edit" : "/aws/user/create";

    await makeRequest(url, opts)
      .then(handleSuccess)
      .catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // go back to the list view and flash a message
    goBack();
    flashMessage(<span>{res.msg}</span>, "success");
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message from the backend or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );
    flashMessage(msg, "danger");
  };

  /**
   * Assign an about sleep template to the user
   * @param id - the template's database primary key
   */
  const selectAboutSleepTemplate = (id: number): void => {
    const selectedTemplate = aboutSleepTemplates.filter(
      (a: AboutSleepTemplate) => a.id === id
    )[0];

    if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);
  };

  /**
   * Get the about sleep template that is selected
   * @returns - the template's database primary key
   */
  const getSelectedAboutSleepTemplate = (): number => {
    return aboutSleepTemplateSelected ? aboutSleepTemplateSelected.id : 0;
  };

  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  };

  // if dittiId is 0, the user is enrolling a new subject
  const buttonText = dittiId ? "Update" : "Create";

  if (loading) {
    return (
      <FormView>
        <Form>
          <SmallLoader />
        </Form>
      </FormView>
    );
  }

  return (
    <FormView>
      <Form>
        <FormTitle>{dittiId ? "Edit " : "Enroll "} Subject</FormTitle>
        <FormRow>
          <FormField>
            <TextField
              id="dittiId"
              type="text"
              placeholder=""
              prefill={state.userPermissionId.replace(studyPrefix, "")}
              label="Ditti ID"
              onKeyup={(text: string) => {
                setState(prev => ({ ...prev, userPermissionId: studyPrefix + text }));
              }}
              feedback="">
                {/* superimpose the study prefix on the form field */}
                <div className="flex items-center text-[#666699] h-full px-2 bg-light border-r border-light">
                  <i>{studyPrefix}</i>
                </div>
            </TextField>
          </FormField>

          {/* don't allow the user to edit the team email */}
          <FormField>
            <TextField
              label="Team Email"
              prefill={studyEmail}
              disabled={true} />
          </FormField>
        </FormRow>

        {/* the raw timestamp includes ":00.000Z" */}
        <FormRow>
          <FormField>
            <TextField
              id="expiresOn"
              type="datetime-local"
              placeholder=""
              prefill={state.expTime.replace("Z", "")}
              label="Expires On"
              onKeyup={(text: string) =>
                setState(prev => ({ ...prev, expTime: text + ":00.000Z" }))
              }
              feedback="" />
          </FormField>
          <FormField>
            <CheckField
              id="tapping-access"
              prefill={state.tapPermission}
              label="Tapping Access"
              onChange={(val) => setState(prev => ({ ...prev, tapPermission: val }))} />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <div className="mb-1">About Sleep Template</div>
            <div className="border-light">
              <Select
                id={0}
                opts={aboutSleepTemplates.map(
                  (a: AboutSleepTemplate) => {
                    return { value: a.id, label: a.name };
                  }
                )}
                placeholder="Select template..."
                callback={selectAboutSleepTemplate}
                getDefault={getSelectedAboutSleepTemplate} />
            </div>
          </FormField>
        </FormRow>
      </Form>

      <FormSummary>
        <FormSummaryTitle>Subject Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Ditti ID:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{state.userPermissionId}
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
            {state.expTime
              ? new Date(state.expTime).toLocaleDateString("en-US", dateOptions)
              : ""}
            <br />
            <br />
            Tapping access:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{state.tapPermission ? "Yes" : "No"}
            <br />
            <br />
            About sleep template:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{aboutSleepTemplateSelected.name}
            <br />
          </FormSummaryText>
          <div>
            <FormSummaryButton>
              <AsyncButton onClick={post}>{buttonText}</AsyncButton>
            </FormSummaryButton>
            <FormSummarySubtext>
              After enrolling a subject, log in on your smartphone using their
              Ditti ID to ensure their account was created successfully.
            </FormSummarySubtext>
          </div>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};

export default SubjectsEdit;
