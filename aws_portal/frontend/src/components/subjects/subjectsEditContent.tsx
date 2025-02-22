/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { useState, useEffect, createRef, FocusEvent, useRef } from "react";
import TextField from "../fields/textField";
import { AboutSleepTemplate, ResponseBody } from "../../interfaces";
import { formatDateForInput, getEnrollmentInfoForStudy, makeRequest } from "../../utils";
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


/**
 * @property {"ditti" | "wearable"} app - The app (Ditti or Wearable)
 */
interface ISubjectsEditContentProps {
  app: "ditti" | "wearable";
}


/**
 * For validating Cognito password requirements.
 */
const cognitoPasswordValidation = {
  isMinLen: false,  // At least 8 characters
};


/**
 * Regular expressions for password validation
 */
const numberRegex = /\d/;
const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;
const uppercaseRegex = /[A-Z]/;
const lowercaseRegex = /[a-z]/;


const SubjectsEditContent = ({ app }: ISubjectsEditContentProps) => {
  const [searchParams] = useSearchParams();
  const dittiId = searchParams.get("dittiId") || "";

  const [tapPermission, setTapPermission] = useState(false);
  const [information, setInformation] = useState("");
  const [userPermissionId, setUserPermissionId] = useState("");
  const [userPermissionIdFeedback, setUserPermissionIdFeedback] = useState("");
  const [temporaryPassword, setTemporaryPassword] = useState("");
  const [temporaryPasswordValidation, setTemporaryPasswordValidation] = useState(cognitoPasswordValidation);
  const [dittiExpTime, setDittiExpTime] = useState("");
  const [enrollmentStart, setEnrollmentStart] = useState("");
  const [enrollmentStartFeedback, setEnrollmentStartFeedback] = useState("");
  const [enrollmentEnd, setEnrollmentEnd] = useState("");
  const [enrollmentEndFeedback, setEnrollmentEndFeedback] = useState("");
  const [dittiExpTimeFeedback, setDittiExpTimeFeedback] = useState("");
  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<AboutSleepTemplate[]>([]);
  const [aboutSleepTemplateSelected, setAboutSleepTemplateSelected] = useState<AboutSleepTemplate>({} as AboutSleepTemplate);
  const [formIsValid, setFormIsValid] = useState(false);
  const [loading, setLoading] = useState<boolean>(true);

  const previewRef = createRef<HTMLDivElement>();
  const dittiIdInputRef = createRef<HTMLInputElement>();

  const { studiesLoading, study } = useStudiesContext();
  const { studySubjectLoading, getStudySubjectByDittiId, fetchStudySubjects } = useCoordinatorStudySubjectContext();

  const { flashMessage } = useFlashMessageContext();
  const navigate = useNavigate();

  const studySubject = dittiId ? getStudySubjectByDittiId(dittiId) : null;
  const userPermissionIdRef = useRef(userPermissionId);

  // Update the ref whenever userPermissionId changes
  useEffect(() => {
    userPermissionIdRef.current = userPermissionId;
  }, [userPermissionId]);

  const validateForm = () => {
    let isValid = true;
    const today = formatDateForInput(new Date());

    // Only validate password when creating a new study subject
    if (!studySubject) {
      const updatedTemporaryPasswordValidation = { ...cognitoPasswordValidation };

      if (temporaryPassword.length < 8) {
        updatedTemporaryPasswordValidation.isMinLen = false;
        isValid = false;
      } else {
        updatedTemporaryPasswordValidation.isMinLen = true;
      }

      setTemporaryPasswordValidation(updatedTemporaryPasswordValidation);
    }

    if (userPermissionIdRef.current === "") {
      isValid = false;
      setUserPermissionIdFeedback("Ditti ID is required.");
    } else {
      setUserPermissionIdFeedback("");
    }

    if (/\D/.test(userPermissionId)) {
      isValid = false;
      setUserPermissionIdFeedback("Ditti ID must contain only numbers.");
    } else {
      setUserPermissionIdFeedback("");
    }

    if (dittiExpTime < enrollmentEnd) {
      setDittiExpTimeFeedback("Ditti ID expiry date must be after enrollment end date.");
      isValid = false;
    } else {
      setDittiExpTimeFeedback("");
    }

    if (enrollmentEnd <= enrollmentStart) {
      setEnrollmentStartFeedback("Enrollment end date must be after enrollment start date.");
      setEnrollmentEndFeedback("Enrollment end date must be after enrollment start date.");
      isValid = false;
    } else {
      setEnrollmentStartFeedback("");
      setEnrollmentEndFeedback("");
    }

    if (enrollmentEnd <= today) {
      setEnrollmentEndFeedback("Enrollment end date must be a future date.");
      isValid = false;
    } else {
      setEnrollmentEndFeedback("");
    }
  
    setFormIsValid(isValid);
  };

  // Add event listeners for validating Ditti ID field
  useEffect(() => {
    if (dittiIdInputRef.current) {
      dittiIdInputRef.current.addEventListener("blur", validateForm);
      return () => dittiIdInputRef.current?.removeEventListener("blur", validateForm);
    }
  }, [dittiIdInputRef]);


  // Validate the form and set any error messages
  useEffect(validateForm, [
    enrollmentStart,
    enrollmentEnd,
    dittiExpTime,
    userPermissionId,
    temporaryPassword,
  ]);

  // Sanitize the about sleep template and set the preview
  useEffect(() => {
    if (previewRef.current && information !== "") {
      previewRef.current.innerHTML = sanitize(information);
    }
  }, [previewRef]);

  // Load any data to prefill the form with, if any
  useEffect(() => {
    if (studySubject) {
      const { startsOn, expiresOn } = getEnrollmentInfoForStudy(studySubject, study?.id);

      const selectedTemplate = aboutSleepTemplates.filter(
        (ast: AboutSleepTemplate) => ast.text === studySubject.information
      )[0];

      if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);

      setTapPermission(studySubject.tapPermission);
      setInformation(studySubject.information);
      setUserPermissionId(studySubject.dittiId.replace(study?.dittiId || "", ""));
      setDittiExpTime(formatDateForInput(new Date(studySubject.dittiExpTime.replace("Z", ""))));
      setEnrollmentStart(formatDateForInput(startsOn));
      setEnrollmentEnd(formatDateForInput(expiresOn));
    } else {
      const startsOn = new Date();
      const expiresOn = new Date();
      const expiryDelta = study?.defaultExpiryDelta || 14;
      expiresOn.setDate(expiresOn.getDate() + expiryDelta);
      setEnrollmentStart(formatDateForInput(startsOn));
      setEnrollmentEnd(formatDateForInput(expiresOn));
      setDittiExpTime(formatDateForInput(expiresOn));
    }
  }, [studySubject]);

  // Fetch about sleep templates from the database
  useEffect(() => {
    // get all about sleep templates
    const fetchTemplates = makeRequest("/db/get-about-sleep-templates").then(
      (templates: AboutSleepTemplate[]) => setAboutSleepTemplates(templates)
    );
    // when all promises finish, hide the loader
    Promise.all([fetchTemplates]).then(() => setLoading(false));
  }, []);

  // Update the preview when an about sleep template is selected
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
   * POST changes to the backend. Make a request to create an entry if creating a new entry, else make a request to edit
   * an exiting entry. One request is made to the AWS backend and another to the database backend. Another request is
   * made to the Cognito backend if a new participant is being enrolled.
   */
  const post = async (): Promise<void> => {
    // Prepare and make the request to the AWS backend
    const dataAWS = {
      tap_permission: tapPermission,
      information: aboutSleepTemplateSelected.text,
      user_permission_id: study?.dittiId + userPermissionId,
      exp_time: dittiExpTime + "T00:00:00.000Z",
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

    // Prepare and make the request to the database backend
    const { didConsent } = studySubject ?
      getEnrollmentInfoForStudy(studySubject, study?.id)
      : { didConsent: false};

    const dataDB = {
      ditti_id: study?.dittiId + userPermissionId,
      studies: [
        {
          id: study?.id || 0,
          starts_on: enrollmentStart + "T00:00:00.000Z",
          expires_on: enrollmentEnd + "T00:00:00.000Z",
          did_consent: didConsent,
        }
      ]
    };

    const bodyDB = {
      app: app === "ditti" ? 2 : 3,
      study: study?.id || 0,
      ...(studySubject ? { id: studySubject.id, edit: dataDB } : { create: dataDB })
    };

    const optsDB = { method: "POST", body: JSON.stringify(bodyDB) };
    const urlDB = studySubject ? "/admin/study_subject/edit" : "/admin/study_subject/create";
    const postDB = makeRequest(urlDB, optsDB);

    const promises: Promise<ResponseBody>[] = [postAWS, postDB];

    // If enrolling a new participant, make a request to the Cognito backend
    if (!studySubject) {
      const bodyCognito = {
        app: app === "ditti" ? 2 : 3,
        study: study?.id || 0,
        data: {
          cognitoUsername: study?.dittiId + userPermissionId,
          temporaryPassword: temporaryPassword,
        },
      };

      const optsCognito = { method: "POST", body: JSON.stringify(bodyCognito) };
      const urlCognito = "/cognito/register/participant";
      const postCognito = makeRequest(urlCognito, optsCognito);
      promises.push(postCognito);
    }

    await Promise.all(promises)
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
  };

  // If dittiId is 0, the user is enrolling a new subject
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
              value={userPermissionId}
              label="Ditti ID"
              onKeyup={text => setUserPermissionId(text)}
              feedback={userPermissionIdFeedback}
              required={true}
              inputRef={dittiIdInputRef}
              disabled={Boolean(studySubject)}>
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

        {!studySubject &&
          <>
            <FormRow>
              <FormField>
                <TextField
                  id="temporary-password"
                  type="password"
                  placeholder=""
                  value={temporaryPassword}
                  label="Temporary Password"
                  onKeyup={setTemporaryPassword}
                  required={true} />
                <div className="flex flex-col">
                  <span className={`text-sm ${temporaryPasswordValidation.isMinLen ? "text-[green]" : "text-[red]"}`}>Must be 8 at least characters</span>
                </div>
              </FormField>
            </FormRow>
          </>
        }

        {/* the raw timestamp includes ":00.000Z" */}
        <FormRow>
          <FormField>
            <TextField
              id="enrollment-start"
              type="date"
              placeholder=""
              value={enrollmentStart}
              label="Enrollment Start Date"
              onKeyup={setEnrollmentStart}
              feedback={enrollmentStartFeedback}
              required={true} />
          </FormField>
          <FormField>
            <TextField
              id="enrollment-end"
              type="date"
              placeholder=""
              value={enrollmentEnd}
              label="Enrollment End Date"
              onKeyup={setEnrollmentEnd}
              feedback={enrollmentEndFeedback}
              required={true} />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <TextField
              id="ditti-expiry"
              type="date"
              placeholder=""
              value={dittiExpTime}
              label="Ditti ID Expiry Date"
              onKeyup={setDittiExpTime}
              feedback={dittiExpTimeFeedback}
              required={true} />
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
            &nbsp;&nbsp;&nbsp;&nbsp;{study?.dittiId + userPermissionId}
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
              disabled={APP_ENV === "demo" || !formIsValid}>
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
