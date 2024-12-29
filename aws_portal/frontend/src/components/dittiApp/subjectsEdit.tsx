import React, { useState, useEffect, createRef } from "react";
import TextField from "../fields/textField";
import {
  AboutSleepTemplate,
  IStudySubjectDetails,
  ResponseBody,
  Study,
  StudySubjectPrefill,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { getStartAndExpiryTimes, makeRequest } from "../../utils";
import CheckField from "../fields/checkField";
import { SmallLoader } from "../loader";
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
import { APP_ENV } from "../../environment";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import sanitize from "sanitize-html";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { useSearchParams } from "react-router-dom";
import { useStudiesContext } from "../../contexts/studiesContext";

const SubjectsEdit = () => {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;
  const dittiId = searchParams.get("dittiId");

  const [tapPermission, setTapPermission] = useState(false);
  const [information, setInformation] = useState("");
  const [userPermissionId, setUserPermissionId] = useState("");
  const [startTime, setStartTime] = useState("");
  const [expTime, setExpTime] = useState("");
  const [teamEmail, setTeamEmail] = useState("");
  const [createdAt, setCreatedAt] = useState("");

  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<AboutSleepTemplate[]>([]);
  const [aboutSleepTemplateSelected, setAboutSleepTemplateSelected] = useState<AboutSleepTemplate>({} as AboutSleepTemplate);
  const [loading, setLoading] = useState<boolean>(true);
  const previewRef = createRef<HTMLDivElement>();
  
  const { studiesLoading, getStudyById } = useStudiesContext();
  const { getStudySubjectByDittiId } = useCoordinatorStudySubjectContext();

  const study = getStudyById(studyId);

  useEffect(() => {
    if (previewRef.current && information !== "") {
      previewRef.current.innerHTML = sanitize(information);
    }
  }, [previewRef]);

  useEffect(() => {
    // get all about sleep templates
    const fetchTemplates = makeRequest("/db/get-about-sleep-templates").then(
      (templates: AboutSleepTemplate[]) => setAboutSleepTemplates(templates)
    );

    // get the form's prefill
    const prefill = getPrefill();
    setTapPermission(prefill.tapPermission);
    setInformation(prefill.information);
    setUserPermissionId(prefill.dittiId);
    setExpTime(prefill.expTime);

    // when all promises finish, hide the loader
    Promise.all([fetchTemplates]).then(() => setLoading(false));
  }, [dittiId]);

  useEffect(() => {
    if (previewRef.current) {
      if (aboutSleepTemplateSelected.text) {
        previewRef.current.innerHTML = sanitize(aboutSleepTemplateSelected.text);
      } else {
        previewRef.current.innerHTML = sanitize(information);
      }
    }
  }, [aboutSleepTemplateSelected]);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = (): StudySubjectPrefill => {
    if (dittiId) {
      return makePrefill(getStudySubjectByDittiId(dittiId));
    }

    return {
      tapPermission: false,
      information: "",
      dittiId: "",
      startTime: (new Date()).toISOString().replace("Z", ""),
      expTime: "",
    }
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (studySubject: IStudySubjectDetails): StudySubjectPrefill => {
    const selectedTemplate = aboutSleepTemplates.filter(
      (ast: AboutSleepTemplate) => ast.text === studySubject.information
    )[0];
    if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);
    const { startTime, expTime } = getStartAndExpiryTimes(studySubject, studyId);

    return {
      tapPermission: studySubject.tapPermission,
      information: studySubject.information,
      dittiId: studySubject.dittiId,
      startTime,
      expTime,
    };
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async (): Promise<void> => {
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
    // goBack();
    // flashMessage(<span>{res.msg}</span>, "success");
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
    // flashMessage(msg, "danger");
  };

  /**
   * Assign an about sleep template to the user
   * @param id - the template's database primary key
   */
  const selectAboutSleepTemplate = (id: number): void => {
    const selectedTemplate = aboutSleepTemplates.filter(
      (a: AboutSleepTemplate) => a.id === id
    )[0];

    if (selectedTemplate) {
      setAboutSleepTemplateSelected(selectedTemplate);
    } else {
      setAboutSleepTemplateSelected({} as AboutSleepTemplate);
    }
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

  if (loading || studiesLoading) {
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
              value={userPermissionId.replace(study?.dittiId || "", "")}
              label="Ditti ID"
              onKeyup={text => setUserPermissionId(study?.dittiId + text)}
              feedback="">
                {/* superimpose the study prefix on the form field */}
                <div className="flex items-center text-link h-full px-2 bg-extra-light border-r border-light">
                  <i>{study?.dittiId}</i>
                </div>
            </TextField>
          </FormField>

          {/* don't allow the user to edit the team email */}
          <FormField>
            <TextField
              label="Team Email"
              value={study?.email || ""}
              disabled={true} />
          </FormField>
        </FormRow>

        {/* the raw timestamp includes ":00.000Z" */}
        <FormRow>
          <FormField>
            <TextField
              id="startsOn"
              type="datetime-local"
              placeholder=""
              value={expTime.replace("Z", "")}
              label="Expires On"
              onKeyup={text => setExpTime(text + ":00.000Z")}
              feedback="" />
          </FormField>
          <FormField>
            <TextField
              id="expiresOn"
              type="datetime-local"
              placeholder=""
              value={expTime.replace("Z", "")}
              label="Expires On"
              onKeyup={text => setExpTime(text + ":00.000Z")}
              feedback="" />
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
          <FormField>
            <CheckField
              id="tapping-access"
              prefill={tapPermission}
              label="Tapping Access"
              onChange={setTapPermission} />
          </FormField>
        </FormRow>
        <FormTitle className="mt-6">About Sleep Template Preview</FormTitle>
        <FormRow>
          <div ref={previewRef} className="px-4" />
        </FormRow>
      </Form>

      <FormSummary>
        <FormSummaryTitle>Subject Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Ditti ID:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{userPermissionId}
            <br />
            <br />
            Team email:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{study?.email}
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
          </FormSummaryText>
          <div>
            <FormSummaryButton
              onClick={post}
              disabled={APP_ENV === "demo"}>
                {buttonText}
            </FormSummaryButton>
            {APP_ENV === "demo" &&
              <FormSummarySubtext>
                {dittiId ?
                  "Updating users is disabled in demo mode." :
                  "Enrolling new users is disabled in demo mode."
                }
              </FormSummarySubtext>
            }
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
