/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { useState, useEffect, createRef, useRef, useCallback } from "react";
import { TextField } from "../fields/textField";
import { AboutSleepTemplate, ResponseBody } from "../../types/api";
import { formatDateForInput, getEnrollmentInfoForStudy } from "../../utils";
import { httpClient } from "../../lib/http";
import { CheckField } from "../fields/checkField";
import { SmallLoader } from "../loader/loader";
import { SelectField } from "../fields/selectField";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormSummary } from "../containers/forms/formSummary";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import { FormSummarySubtext } from "../containers/forms/formSummarySubtext";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { APP_ENV } from "../../environment";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useStudies } from "../../hooks/useStudies";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { QuillView } from "../containers/quillView/quillView";
import { SubjectsEditContentProps } from "./subjects.types";
import { useApiHandler } from "../../hooks/useApiHandler";

/**
 * For validating Cognito password requirements.
 */
const cognitoPasswordValidation = {
  isMinLen: false, // At least 8 characters
};

export const SubjectsEditContent = ({ app }: SubjectsEditContentProps) => {
  const [searchParams] = useSearchParams();
  const dittiId = searchParams.get("dittiId") ?? "";

  const [tapPermission, setTapPermission] = useState(false);
  const [information, setInformation] = useState("");
  const [userPermissionId, setUserPermissionId] = useState("");
  const [userPermissionIdFeedback, setUserPermissionIdFeedback] = useState("");
  const [temporaryPassword, setTemporaryPassword] = useState("");
  const [temporaryPasswordValidation, setTemporaryPasswordValidation] =
    useState(cognitoPasswordValidation);
  const [dittiExpTime, setDittiExpTime] = useState("");
  const [enrollmentStart, setEnrollmentStart] = useState("");
  const [enrollmentStartFeedback, setEnrollmentStartFeedback] = useState("");
  const [enrollmentEnd, setEnrollmentEnd] = useState("");
  const [enrollmentEndFeedback, setEnrollmentEndFeedback] = useState("");
  const [dittiExpTimeFeedback, setDittiExpTimeFeedback] = useState("");
  const [aboutSleepTemplates, setAboutSleepTemplates] = useState<
    AboutSleepTemplate[]
  >([]);
  const [aboutSleepTemplateSelected, setAboutSleepTemplateSelected] =
    useState<AboutSleepTemplate>({} as AboutSleepTemplate);
  const [formIsValid, setFormIsValid] = useState(false);

  const dittiIdInputRef = createRef<HTMLInputElement>();

  const { studiesLoading, study } = useStudies();
  const { studySubjectLoading, getStudySubjectByDittiId, fetchStudySubjects } =
    useCoordinatorStudySubjects();

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  const studySubject = dittiId ? getStudySubjectByDittiId(dittiId) : null;
  const userPermissionIdRef = useRef(userPermissionId);

  // Update the ref whenever userPermissionId changes
  useEffect(() => {
    userPermissionIdRef.current = userPermissionId;
  }, [userPermissionId]);

  const { safeRequest: safeFetchTemplates, isLoading: isLoadingTemplates } =
    useApiHandler<AboutSleepTemplate[]>({
      errorMessage: "Failed to load About Sleep templates.",
      showDefaultSuccessMessage: false,
    });

  const { safeRequest: safeSubmit, isLoading: isSubmitting } = useApiHandler<
    ResponseBody[]
  >({
    // Expects array from Promise.all
    successMessage: (data) =>
      data[0]?.msg ?? "Subject details saved successfully.", // Use msg from first response
    errorMessage: (error) => `Failed to save subject details: ${error.message}`,
    onSuccess: () => {
      fetchStudySubjects(); // Refresh subject list
      navigate(-1); // Navigate back
    },
  });

  const validateForm = useCallback(() => {
    let isValid = true;
    const today = formatDateForInput(new Date());

    // Only validate password when creating a new study subject
    if (!studySubject) {
      const updatedTemporaryPasswordValidation = {
        ...cognitoPasswordValidation,
      };

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
      setUserPermissionIdFeedback("Ditti ID suffix is required.");
    } else if (/[^0-9]/.test(userPermissionIdRef.current)) {
      isValid = false;
      setUserPermissionIdFeedback("Ditti ID suffix must contain only numbers.");
    } else {
      setUserPermissionIdFeedback("");
    }

    if (dittiExpTime < enrollmentEnd && enrollmentEnd && dittiExpTime) {
      setDittiExpTimeFeedback(
        "Ditti ID expiry date must be after enrollment end date."
      );
      isValid = false;
    } else {
      setDittiExpTimeFeedback("");
    }

    if (enrollmentEnd <= enrollmentStart && enrollmentStart && enrollmentEnd) {
      setEnrollmentStartFeedback(
        "Enrollment end date must be after enrollment start date."
      );
      setEnrollmentEndFeedback(
        "Enrollment end date must be after enrollment start date."
      );
      isValid = false;
    } else {
      if (
        !(enrollmentEnd <= enrollmentStart && enrollmentStart && enrollmentEnd)
      ) {
        setEnrollmentStartFeedback("");
      }
      setEnrollmentEndFeedback("");
    }

    if (enrollmentEnd <= today && enrollmentEnd) {
      setEnrollmentEndFeedback("Enrollment end date must be a future date.");
      isValid = false;
    } else if (!enrollmentEndFeedback) {
      setEnrollmentEndFeedback("");
    }

    setFormIsValid(isValid);
  }, [
    temporaryPassword,
    userPermissionIdRef,
    dittiExpTime,
    enrollmentEnd,
    enrollmentStart,
    studySubject,
    enrollmentEndFeedback,
  ]);

  // Validate the form and set any error messages
  useEffect(() => {
    validateForm();
  }, [
    enrollmentStart,
    enrollmentEnd,
    dittiExpTime,
    userPermissionId,
    temporaryPassword,
    validateForm,
  ]);

  // Load any data to prefill the form with, if any
  useEffect(() => {
    if (studySubject) {
      const { startsOn, expiresOn } = getEnrollmentInfoForStudy(
        studySubject,
        study?.id
      );

      const selectedTemplate = aboutSleepTemplates.find(
        (ast: AboutSleepTemplate) => ast.text === studySubject.information
      );

      if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);

      setTapPermission(studySubject.tapPermission);
      setInformation(studySubject.information);
      setUserPermissionId(
        studySubject.dittiId.replace(study?.dittiId ?? "", "")
      );
      setDittiExpTime(
        formatDateForInput(new Date(studySubject.dittiExpTime.replace("Z", "")))
      );
      setEnrollmentStart(formatDateForInput(startsOn));
      setEnrollmentEnd(formatDateForInput(expiresOn));
    } else {
      const startsOn = new Date();
      const expiresOn = new Date();
      const expiryDelta = study?.defaultExpiryDelta ?? 14;
      expiresOn.setDate(expiresOn.getDate() + expiryDelta);
      setEnrollmentStart(formatDateForInput(startsOn));
      setEnrollmentEnd(formatDateForInput(expiresOn));
      setDittiExpTime(formatDateForInput(expiresOn));
      setTapPermission(false);
      setInformation("");
      setUserPermissionId("");
      setTemporaryPassword("");
      setAboutSleepTemplateSelected({} as AboutSleepTemplate);
    }
  }, [
    studySubject,
    study?.id,
    study?.dittiId,
    study?.defaultExpiryDelta,
    aboutSleepTemplates,
  ]);

  // Fetch about sleep templates from the database
  useEffect(() => {
    const fetchTemplates = async () => {
      const response = await safeFetchTemplates(async () => {
        return httpClient.request<AboutSleepTemplate[]>(
          `/db/get-about-sleep-templates?app=${String(app === "ditti" ? 2 : 3)}`
        );
      });

      if (response) {
        setAboutSleepTemplates(response);
        if (studySubject && response.length > 0) {
          const selectedTemplate = response.find(
            (ast: AboutSleepTemplate) => ast.text === studySubject.information
          );
          if (selectedTemplate) setAboutSleepTemplateSelected(selectedTemplate);
        } else if (!studySubject && response.length > 0) {
          // Optionally set a default template when creating new subject
          // setAboutSleepTemplateSelected(response[0]);
        }
      }
    };
    void fetchTemplates();
  }, [app, safeFetchTemplates, studySubject]);

  /**
   * POST changes to the backend. Make a request to create an entry if creating a new entry, else make a request to edit
   * an exiting entry. One request is made to the AWS backend and another to the database backend. Another request is
   * made to the Cognito backend if a new participant is being enrolled.
   */
  const post = async () => {
    if (!formIsValid) {
      flashMessage(
        <span>Please correct the errors in the form before submitting.</span>,
        "danger"
      );
      return;
    }

    const fullDittiId = (study?.dittiId ?? "") + userPermissionId;

    // Prepare data for AWS
    const dataAWS = {
      tap_permission: tapPermission,
      information: aboutSleepTemplateSelected.text,
      user_permission_id: fullDittiId,
      exp_time: dittiExpTime + "T00:00:00.000Z",
      team_email: study?.email,
    };
    const bodyAWS = {
      app: app === "ditti" ? 2 : 3,
      study: study?.id ?? 0,
      ...(dittiId
        ? { user_permission_id: dittiId, edit: dataAWS }
        : { create: dataAWS }),
    };

    // Prepare data for DB
    const { didConsent } = studySubject
      ? getEnrollmentInfoForStudy(studySubject, study?.id)
      : { didConsent: false };
    const dataDB = {
      ditti_id: fullDittiId,
      studies: [
        {
          id: study?.id ?? 0,
          starts_on: enrollmentStart + "T00:00:00.000Z",
          expires_on: enrollmentEnd + "T00:00:00.000Z",
          did_consent: didConsent,
        },
      ],
    };
    const bodyDB = {
      app: app === "ditti" ? 2 : 3,
      study: study?.id ?? 0,
      ...(studySubject
        ? { id: studySubject.id, edit: dataDB }
        : { create: dataDB }),
    };

    // Prepare Cognito request if creating new user
    const cognitoPromise = async (): Promise<ResponseBody | null> => {
      if (!studySubject) {
        const bodyCognito = {
          app: app === "ditti" ? 2 : 3,
          study: study?.id ?? 0,
          data: {
            cognitoUsername: fullDittiId,
            temporaryPassword: temporaryPassword,
          },
        };
        const urlCognito = "/auth/participant/register/participant";
        return httpClient.request<ResponseBody>(urlCognito, {
          method: "POST",
          data: bodyCognito,
        });
      }
      return Promise.resolve(null); // Resolve with null if not creating
    };

    // Execute all promises via the API handler
    await safeSubmit(async () => {
      const awsPromise = httpClient.request<ResponseBody>(
        dittiId ? "/aws/user/edit" : "/aws/user/create",
        { method: "POST", data: bodyAWS }
      );
      const dbPromise = httpClient.request<ResponseBody>(
        studySubject
          ? "/admin/study_subject/edit"
          : "/admin/study_subject/create",
        { method: "POST", data: bodyDB }
      );
      const cognitoReqPromise = cognitoPromise(); // Invoke the async function

      // Wait for all core requests. Cognito is optional.
      const results = await Promise.all([
        awsPromise,
        dbPromise,
        cognitoReqPromise, // Include the promise result (null if not needed)
      ]);

      // Filter out the potential null result from Cognito before returning
      // Although the hook expects ResponseBody[], we only care about the first for success msg
      return results.filter((res) => res !== null);
    });
  };

  /**
   * Assign an about sleep template to the user
   * @param id - the template's database primary key
   */
  const selectAboutSleepTemplate = (id: number): void => {
    const selectedTemplate = aboutSleepTemplates.find(
      (a: AboutSleepTemplate) => a.id === id
    );

    if (selectedTemplate) {
      setAboutSleepTemplateSelected(selectedTemplate);
      setInformation(selectedTemplate.text);
    } else {
      setAboutSleepTemplateSelected({} as AboutSleepTemplate);
      setInformation("");
    }
  };

  /**
   * Get the about sleep template that is selected
   * @returns - the template's database primary key
   */
  const getSelectedAboutSleepTemplate = (): number => {
    return aboutSleepTemplateSelected.id || 0;
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
    : "";
  const enrollmentEndFormatted = enrollmentEnd
    ? new Date(enrollmentEnd).toLocaleDateString("en-US", dateOptions)
    : "";

  // Combine loading states
  const combinedLoading =
    isLoadingTemplates || studiesLoading || studySubjectLoading;

  if (combinedLoading) {
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
              onKeyup={(text) => {
                setUserPermissionId(text);
              }}
              feedback={userPermissionIdFeedback}
              required={true}
              inputRef={dittiIdInputRef}
              disabled={Boolean(studySubject)}
            >
              {/* superimpose the study prefix on the form field */}
              <div
                className="flex h-full items-center border-r border-light
                  bg-extra-light px-2 text-link"
              >
                <i>{study?.dittiId}</i>
              </div>
            </TextField>
          </FormField>

          {/* don't allow the user to edit the team email */}
          <FormField>
            <TextField
              label="Team Email"
              value={study?.email ?? ""}
              disabled={true}
            />
          </FormField>
        </FormRow>

        {!studySubject && (
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
                  required={true}
                />
                <div className="flex flex-col">
                  <span
                    className={`text-sm
                    ${temporaryPasswordValidation.isMinLen ? "text-[green]" : "text-[red]"}`}
                  >
                    Must be 8 at least characters
                  </span>
                </div>
              </FormField>
            </FormRow>
          </>
        )}

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
              required={true}
            />
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
              required={true}
            />
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
              required={true}
            />
          </FormField>
          <FormField>
            <CheckField
              id="tapping-access"
              prefill={tapPermission}
              label="Tapping Access"
              onChange={setTapPermission}
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <div className="mb-1">About Sleep Template</div>
            <div className="border-light">
              <SelectField
                id={0}
                opts={aboutSleepTemplates.map((a: AboutSleepTemplate) => {
                  return { value: a.id, label: a.name };
                })}
                placeholder="Select template..."
                callback={selectAboutSleepTemplate}
                getDefault={getSelectedAboutSleepTemplate}
              />
            </div>
          </FormField>
        </FormRow>
        <FormTitle className="mt-6">About Sleep Template Preview</FormTitle>
        <FormRow>
          <QuillView
            className="px-4"
            content={aboutSleepTemplateSelected.text || information}
          />
        </FormRow>
      </Form>

      <FormSummary>
        <FormSummaryTitle>Subject Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Ditti ID:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{(study?.dittiId ?? "") + userPermissionId}
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
              disabled={APP_ENV === "demo" || !formIsValid || isSubmitting}
            >
              {isSubmitting ? "Saving..." : buttonText}
            </FormSummaryButton>
            {APP_ENV === "demo" && (
              <FormSummarySubtext>
                {dittiId
                  ? "Updating users is disabled in demo mode."
                  : "Enrolling new users is disabled in demo mode."}
              </FormSummarySubtext>
            )}
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
