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

import { useEffect, useState } from "react";
import { TextField } from "../fields/textField";
import { CheckField } from "../fields/checkField";
import { MemoizedQuillField as QuillField } from "../fields/quillField";
import { ResponseBody, Study } from "../../types/api";
import { httpClient } from "../../lib/http";
import { SmallLoader } from "../loader/loader";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormSummary } from "../containers/forms/formSummary";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useApiHandler } from "../../hooks/useApiHandler";

interface StudiesEditFormPrefill {
  name: string;
  acronym: string;
  dittiId: string;
  email: string;
  defaultExpiryDelta: number;
  consentInformation?: string;
  dataSummary?: string;
  isQi: boolean;
}

export const StudiesEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const studyId = id ? parseInt(id) : 0;

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();
  const [name, setName] = useState<string>("");
  const [acronym, setAcronym] = useState<string>("");
  const [dittiId, setDittiId] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [defaultExpiryDelta, setDefaultExpiryDelta] = useState<number>(14);
  const [consentInformation, setConsentInformation] = useState<string>("");
  const [dataSummary, setDataSummary] = useState<string>("");
  const [isQi, setIsQi] = useState<boolean>(false);
  const [expiryError, setExpiryError] = useState<string>("");

  const { safeRequest: safeFetchInitialData, isLoading: isLoadingData } =
    useApiHandler<StudiesEditFormPrefill | null>({
      // Using null to indicate not found or error during fetch
      errorMessage: "Failed to load study data.",
      showDefaultSuccessMessage: false,
    });

  const { safeRequest: safeSubmit, isLoading: isSubmitting } =
    useApiHandler<ResponseBody>({
      successMessage: (data) => data.msg,
      errorMessage: (error) => `Failed to save study: ${error.message}`,
      onSuccess: () => {
        navigate(-1); // Navigate back on success
      },
    });

  useEffect(() => {
    if (studyId === 0) {
      // If creating new, no need to fetch, reset state (though likely already default)
      setName("");
      setAcronym("");
      setDittiId("");
      setEmail("");
      setDefaultExpiryDelta(14);
      setConsentInformation("");
      setDataSummary("");
      setIsQi(false);
      return; // Exit useEffect
    }

    // Fetch prefill data only if editing (studyId is not 0)
    const fetchData = async () => {
      const prefillData = await safeFetchInitialData(async () => {
        const data = await httpClient.request<Study[]>(
          `/admin/study?app=1&id=${String(studyId)}`
        );
        if (data.length > 0) {
          const study = data[0];
          return {
            name: study.name,
            acronym: study.acronym,
            dittiId: study.dittiId,
            email: study.email,
            defaultExpiryDelta: study.defaultExpiryDelta,
            consentInformation: study.consentInformation ?? "",
            dataSummary: study.dataSummary ?? "",
            isQi: study.isQi,
          };
        } else {
          // Study not found for ID
          throw new Error("Study not found or empty response.");
        }
      });

      // Update state if fetch was successful
      if (prefillData) {
        setName(prefillData.name);
        setAcronym(prefillData.acronym);
        setDittiId(prefillData.dittiId);
        setEmail(prefillData.email);
        setDefaultExpiryDelta(prefillData.defaultExpiryDelta);
        setConsentInformation(prefillData.consentInformation ?? "");
        setDataSummary(prefillData.dataSummary ?? "");
        setIsQi(prefillData.isQi);
      } else {
        // Handle fetch failure (error message shown by hook)
        // Navigate back as the study couldn't be loaded
        navigate(-1);
      }
    };

    void fetchData();
  }, [studyId, safeFetchInitialData, navigate]); // Dependencies for fetching

  /**
   * Ensure that defaultExpiryDelta is non-negative
   */
  useEffect(() => {
    if (defaultExpiryDelta < 0) {
      setDefaultExpiryDelta(0);
      setExpiryError("Default Enrollment Period must be nonnegative.");
    } else {
      setExpiryError("");
    }
  }, [defaultExpiryDelta]);

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async () => {
    // Basic Validations
    if (!name.trim() || !acronym.trim() || !dittiId.trim() || !email.trim()) {
      flashMessage(
        <span>All fields except Consent/Data Summary are required.</span>,
        "danger"
      );
      return;
    }
    if (expiryError) {
      flashMessage(<span>Please fix the validation errors.</span>, "danger");
      return;
    }

    // Construct the request body
    const data = {
      acronym,
      dittiId,
      email,
      name,
      defaultExpiryDelta,
      consentInformation,
      dataSummary,
      isQi,
    };
    const id = studyId;
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data }),
    };

    const url = id ? "/admin/study/edit" : "/admin/study/create";

    await safeSubmit(() =>
      httpClient.request<ResponseBody>(url, {
        method: "POST",
        data: body, // Use data property
      })
    );
  };

  const buttonText = studyId ? "Update" : "Create";

  if (isLoadingData) {
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
        <FormTitle>{studyId ? "Edit " : "Create "} Study</FormTitle>
        <FormRow>
          <FormField>
            <TextField
              id="name"
              type="text"
              placeholder=""
              value={name}
              label="Name"
              onKeyup={(text: string) => {
                setName(text);
              }}
              feedback=""
            />
          </FormField>
          <FormField>
            <TextField
              id="email"
              type="email"
              placeholder=""
              value={email}
              label="Team Email"
              onKeyup={(text: string) => {
                setEmail(text);
              }}
              feedback=""
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <TextField
              id="acronym"
              type="text"
              placeholder=""
              value={acronym}
              label="Acronym"
              onKeyup={(text: string) => {
                setAcronym(text);
              }}
              feedback=""
            />
          </FormField>
          <FormField>
            <TextField
              id="dittiId"
              type="text"
              placeholder=""
              value={dittiId}
              label="Ditti ID"
              onKeyup={(text: string) => {
                setDittiId(text);
              }}
              feedback=""
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <TextField
              id="defaultExpiryDelta"
              type="number"
              placeholder="14"
              min={0}
              value={defaultExpiryDelta.toString()} // Ensure value is string for input
              label="Default Enrollment Period (days)"
              onKeyup={(text: string) => {
                const value = parseInt(text, 10);
                setDefaultExpiryDelta(isNaN(value) ? 0 : value);
              }}
              feedback={expiryError}
            />
          </FormField>
          <FormField>
            <CheckField
              id="isQi"
              label="Quality Improvement Study?"
              prefill={isQi}
              onChange={setIsQi}
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <QuillField
              id="consentInformation"
              containerClassName="ql-container-form"
              label="Consent Information"
              description="Participants must accept this consent form when connecting their Fitbit API."
              value={consentInformation}
              onChange={setConsentInformation}
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <QuillField
              id="dataSummary"
              containerClassName="ql-container-form"
              label="Data Summary"
              description="This text will appear on the participant dashboard as a brief summary of how their data will be used."
              value={dataSummary}
              onChange={setDataSummary}
            />
          </FormField>
        </FormRow>
      </Form>
      <FormSummary>
        <FormSummaryTitle>Study Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            <b>Name:</b>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name || "[No Name]"}
            <br />
            <br />
            <b>Team Email:</b>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{email || "[No Email]"}
            <br />
            <br />
            <b>Acronym:</b>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{acronym || "[No Acronym]"}
            <br />
            <br />
            <b>Ditti ID:</b>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{dittiId || "[No Ditti ID]"}
            <br />
            <br />
            <b>Default Enrollment Period (days):</b>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{defaultExpiryDelta}
            <br />
            <br />
            <b>Is QI:</b>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{isQi ? "Yes" : "No"}
            <br />
          </FormSummaryText>
          {/* Pass post directly */}
          <FormSummaryButton onClick={post} disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
