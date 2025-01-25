import { useState, useEffect, createRef } from "react";
import TextField from "../fields/textField";
import {
  AboutSleepTemplate,
  IStudySubjectDetails,
  ResponseBody,
  StudySubjectPrefill,
} from "../../interfaces";
import { formatDateForInput, getStartOnAndExpiresOnForStudy, makeRequest } from "../../utils";
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
import sanitize from "sanitize-html";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useStudiesContext } from "../../contexts/studiesContext";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";


interface ISubjectsEditContentProps {
  app: "ditti" | "wearable";
}


const SubjectsEditContent = ({ app }: ISubjectsEditContentProps) => {
  const [searchParams] = useSearchParams();
  const dittiId = searchParams.get("dittiId") || "";

  const [tapPermission, setTapPermission] = useState(false);
  const [information, setInformation] = useState("");
  const [userPermissionId, setUserPermissionId] = useState("");
  const [dittiExpTime, setDittiExpTime] = useState(new Date());
  const [enrollmentStart, setEnrollmentStart] = useState(new Date());
  const [enrollmentEnd, setEnrollmentEnd] = useState(new Date());
  const [enrollmentFeedback, setEnrollmentFeedback] = useState("");
  const [dittiExpTimeFeedback, setDittiExpTimeFeedback] = useState("");

  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<AboutSleepTemplate[]>([]);
  const [aboutSleepTemplateSelected, setAboutSleepTemplateSelected] = useState<AboutSleepTemplate>({} as AboutSleepTemplate);
  const [loading, setLoading] = useState<boolean>(true);
  const previewRef = createRef<HTMLDivElement>();
  
  const { studiesLoading, study } = useStudiesContext();
  const { studySubjectLoading, getStudySubjectByDittiId, fetchStudySubjects } = useCoordinatorStudySubjectContext();

  const { flashMessage } = useFlashMessageContext();
  const navigate = useNavigate();

  const studySubject = dittiId ? getStudySubjectByDittiId(dittiId) : null;

  useEffect(() => {
    if (dittiExpTime <= enrollmentEnd) {
      setDittiExpTimeFeedback("Ditti ID expiry date must be after enrollment end date.")
    } else {
      setDittiExpTimeFeedback("");
    }
  }, [enrollmentEnd, dittiExpTime]);

  useEffect(() => {
    if (enrollmentEnd <= enrollmentStart) {
      setEnrollmentFeedback("Enrollment end date must be after enrollment start date.")
    } else {
      setEnrollmentFeedback("");
    }
    if (dittiExpTime <= enrollmentEnd) {
      setDittiExpTimeFeedback("Ditti ID expiry date must be after enrollment end date.")
    } else {
      setDittiExpTimeFeedback("");
    }
  }, [enrollmentStart, enrollmentEnd, dittiExpTime]);

  useEffect(() => {
    if (previewRef.current && information !== "") {
      previewRef.current.innerHTML = sanitize(information);
    }
  }, [previewRef]);

  useEffect(() => {
    if (studySubject) {
      const { startsOn, expiresOn } = getStartOnAndExpiresOnForStudy(studySubject, study?.id || 0);

      const selectedTemplate = aboutSleepTemplates.filter(
        (ast: AboutSleepTemplate) => ast.text === studySubject.information
      )[0];

      if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);

      setTapPermission(studySubject.tapPermission);
      setInformation(studySubject.information);
      setUserPermissionId(studySubject.dittiId);
      setDittiExpTime(new Date(studySubject.dittiExpTime.replace("Z", "")));
      setEnrollmentStart(startsOn);
      setEnrollmentEnd(expiresOn);
    } else {
      const startsOn = new Date();
      const expiresOn = new Date();
      const expiryDelta = study?.defaultExpiryDelta || 14;
      expiresOn.setDate(expiresOn.getDate() + expiryDelta);
      const dittiExpTime = new Date(expiresOn);
      dittiExpTime.setDate(dittiExpTime.getDate() + 1);
      setEnrollmentStart(startsOn);
      setEnrollmentEnd(expiresOn);
      setDittiExpTime(dittiExpTime);
    }
  }, [studySubject]);

  useEffect(() => {
    // get all about sleep templates
    const fetchTemplates = makeRequest("/db/get-about-sleep-templates").then(
      (templates: AboutSleepTemplate[]) => setAboutSleepTemplates(templates)
    );
    // when all promises finish, hide the loader
    Promise.all([fetchTemplates]).then(() => setLoading(false));
  }, []);

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
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async (): Promise<void> => {
    const dataAWS = {
      tap_permission: tapPermission,
      information: aboutSleepTemplateSelected.text,
      user_permission_id: userPermissionId,
      exp_time: dittiExpTime,
      team_email: study?.email
    };

    const bodyAWS = {
      app: app === "ditti" ? 2 : 3,
      study: study?.id || 0,
      ...(dittiId ? { user_permission_id: dittiId, edit: dataAWS } : { create: dataAWS })
    };

    const optsAWS = { method: "POST", body: JSON.stringify(bodyAWS) };
    const urlAWS = dittiId ? "/aws/user/edit" : "/aws/user/create";
    const postAWS = makeRequest(urlAWS, optsAWS);

    const dataDB = {
      ditti_id: userPermissionId,
      studies: [
        {
          id: study?.id || 0,
          starts_on: enrollmentStart.toISOString(),
          expires_on: enrollmentEnd.toISOString(),
        }
      ]
    }

    const bodyDB = {
      app: app === "ditti" ? 2 : 3,
      study: study?.id || 0,
      ...(studySubject ? { id: studySubject.id, edit: dataDB } : { create: dataDB })
    };

    const optsDB = { method: "POST", body: JSON.stringify(bodyDB) };
    const urlDB = studySubject ? "/admin/study_subject/edit" : "/admin/study_subject/create";
    const postDB = makeRequest(urlDB, optsDB);

    const promises: Promise<ResponseBody>[] = [postAWS, postDB];
    Promise.all(promises)
      .then(([resAWS, _]) => handleSuccess(resAWS))
      .catch(error => handleFailure(error))
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // go back to the list view and flash a message
    fetchStudySubjects();
    navigate(-1);
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
    // hour: "2-digit",
    // minute: "2-digit"
  };

  // if dittiId is 0, the user is enrolling a new subject
  const buttonText = dittiId ? "Update" : "Enroll";
  const enrollmentStartFormatted = enrollmentStart
    ? new Date(enrollmentStart).toLocaleDateString("en-US", dateOptions)
    : ""
  const enrollmentEndFormatted = enrollmentEnd
    ? new Date(enrollmentEnd).toLocaleDateString("en-US", dateOptions)
    : ""

  if (loading || studiesLoading || studySubjectLoading) {
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
              id="enrollment-start"
              type="date"
              placeholder=""
              value={formatDateForInput(enrollmentStart)}
              label="Enrollment Start Date"
              onKeyup={text => setEnrollmentStart(new Date(text))}
              feedback={enrollmentFeedback} />
          </FormField>
          <FormField>
            <TextField
              id="enrollment-end"
              type="date"
              placeholder=""
              value={formatDateForInput(enrollmentEnd)}
              label="Enrollment End Date"
              onKeyup={text => setEnrollmentEnd(new Date(text))}
              feedback={enrollmentFeedback} />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <TextField
              id="ditti-expiry"
              type="date"
              placeholder=""
              value={formatDateForInput(dittiExpTime)}
              label="Ditti ID Expiry Date"
              onKeyup={text => setDittiExpTime(new Date(text))}
              feedback={dittiExpTimeFeedback} />
          </FormField>
          <FormField>
            <CheckField
              id="tapping-access"
              prefill={tapPermission}
              label="Tapping Access"
              onChange={setTapPermission} />
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
            Enrollment Period:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;
            {enrollmentStartFormatted} - {enrollmentEndFormatted}
            <br />
            <br />
            Ditti Expires on:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;
            {dittiExpTime
              ? new Date(dittiExpTime).toLocaleDateString("en-US", dateOptions)
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

export default SubjectsEditContent;
