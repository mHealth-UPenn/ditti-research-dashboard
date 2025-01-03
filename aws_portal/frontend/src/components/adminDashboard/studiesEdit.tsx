import React, { useEffect, useState, createRef } from "react";
import TextField from "../fields/textField";
import { ResponseBody, Study, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import FormView from "../containers/forms/formView";
import Form from "../containers/forms/form";
import FormSummary from "../containers/forms/formSummary";
import FormTitle from "../text/formTitle";
import FormRow from "../containers/forms/formRow";
import FormField from "../containers/forms/formField";
import FormSummaryTitle from "../text/formSummaryTitle";
import FormSummaryText from "../containers/forms/formSummaryText";
import FormSummaryButton from "../containers/forms/formSummaryButton";
import FormSummaryContent from "../containers/forms/formSummaryContent";
import sanitize from "sanitize-html";
import { scaleIdentity } from "d3";

interface StudiesEditProps extends ViewProps {
  studyId: number;
}

const StudiesEdit: React.FC<StudiesEditProps> = ({ studyId, goBack, flashMessage }) => {
  const [name, setName] = useState<string>("");
  const [acronym, setAcronym] = useState<string>("");
  const [dittiId, setDittiId] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [defaultExpiryDelta, setDefaultExpiryDelta] = useState<number>(14);
  const [consentInformation, setConsentInformation] = useState<string>("");
  const [dataSummary, setDataSummary] = useState<string>("");
  const [isQi, setIsQi] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [expiryError, setExpiryError] = useState<string>("");

  const consentPreviewRef = createRef<HTMLDivElement>();

  useEffect(() => {
    // Fetch prefill data if editing an existing study
    const fetchPrefill = async () => {
      try {
        const prefillData = await getPrefill();
        setName(prefillData.name);
        setAcronym(prefillData.acronym);
        setDittiId(prefillData.dittiId);
        setEmail(prefillData.email);
        setDefaultExpiryDelta(prefillData.defaultExpiryDelta);
        setConsentInformation(prefillData.consentInformation || "");
        setDataSummary(prefillData.dataSummary || "");
        setIsQi(prefillData.isQi);
      } catch (error) {
        console.error("Error fetching study data:", error);
        flashMessage(
          <span>
            <b>Failed to load study data.</b>
            <br />
            {error instanceof Error ? error.message : "Unknown error"}
          </span>,
          "danger"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPrefill();
  }, [studyId, flashMessage]);

  // Sanitize and set consentInformation in the preview
  useEffect(() => {
    if (consentPreviewRef.current && consentInformation !== "") {
      consentPreviewRef.current.innerHTML = sanitize(consentInformation);
    }
  }, [consentInformation, consentPreviewRef]);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<{
    name: string; 
    acronym: string; 
    dittiId: string; 
    email: string;
    defaultExpiryDelta: number;
    consentInformation?: string;
    dataSummary?: string;
    isQi: boolean;
  }> => {
    if (studyId === 0) {
      // Creating a new study, return empty prefill data
      return {
        name: "",
        acronym: "",
        dittiId: "",
        email: "",
        defaultExpiryDelta: 14,
        consentInformation: "",
        dataSummary: "",
        isQi: false,
      };
    }

    // Fetch existing study data from the backend
    const data: Study[] = await makeRequest(`/admin/study?app=1&id=${studyId}`);
    if (!data || data.length === 0) {
      throw new Error("Study not found.");
    }

    const study = data[0];
    return {
      name: study.name,
      acronym: study.acronym,
      dittiId: study.dittiId,
      email: study.email,
      defaultExpiryDelta: study.defaultExpiryDelta,
      consentInformation: study.consentInformation,
      dataSummary: study.dataSummary,
      isQi: study.isQi
    };
  };

  /**
   * Validate the form field(s)
   * @returns - boolean indicating if the form is valid
   */
  const validateForm = (): boolean => {
    let valid = true;

    // Validate Default Expiry Delta
    if (defaultExpiryDelta < 0) {
      setExpiryError("Default Expiry Time must be nonnegative.");
      valid = false;
    } else {
      setExpiryError("");
    }

    return valid;
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async (): Promise<void> => {
    if (!validateForm()) {
      flashMessage(
        <span>
          <b>Please fix the errors in the form before submitting.</b>
        </span>,
        "danger"
      );
      return;
    }

    const data = { 
      acronym, 
      dittiId, 
      email, 
      name,
      defaultExpiryDelta,
      consentInformation,
      dataSummary,
      isQi
    };
    const id = studyId;
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data }),
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id ? "/admin/study/edit" : "/admin/study/create";

    try {
      const response: ResponseBody = await makeRequest(url, opts);
      handleSuccess(response);
    } catch (error) {
      handleFailure(error as ResponseBody);
    }
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

  const buttonText = studyId ? "Update" : "Create";

  if (loading) {
    return (
      <FormView>
        <Form>
          <SmallLoader />
        </Form>
      </FormView>
    );
  }
  // TODO: No preview on the right hand side. Instead
  // TODO: Add one preview for both consentInformation and dataSummary at the bottom of the form similiar to About Sleep Template Preview
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
              onKeyup={(text: string) => setName(text)}
              feedback=""
            />
          </FormField>
          <FormField>
            <TextField
              id="email"
              type="email" // Changed type to 'email' for better validation
              placeholder=""
              value={email}
              label="Team Email"
              onKeyup={(text: string) => setEmail(text)}
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
              onKeyup={(text: string) => setAcronym(text)}
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
              onKeyup={(text: string) => setDittiId(text)}
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
              // TODO: min may not work because it is a managed text field, possibly fix with useEffect
              min="0"
              value={defaultExpiryDelta.toString()}
              label="Default Expiry Time (days)"
              onKeyup={(text: string) => {
                const value = parseInt(text, 10);
                setDefaultExpiryDelta(isNaN(value) ? 0 : value);
              }}
              feedback={expiryError}
            />
          </FormField>
          <FormField>
            <label htmlFor="isQi" className="mb-1 block">
              Quality Improvement Study?
            </label>
            <div className="flex items-center h-[2.75rem] border border-light p-2">
              {/* TODO: Use textField instead? */}
              <input
                id="isQi"
                type="checkbox"
                checked={isQi}
                onChange={(e) => setIsQi(e.target.checked)}
              />
            </div>
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            {/* TODO: " Desc: This is the consent form that the participant must accept to when connecting their Fitbit API" */}
            <TextField
              id="consentInformation"
              type="textarea"
              placeholder=""
              value={consentInformation}
              label="Consent Information"
              onKeyup={(text: string) => setConsentInformation(text)}
              feedback=""
            />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            {/* TODO: Desc: This text will be shown on the participant dashboard as a brief summary of how their data will be used */}
            {/* Sanitize this as html as well */}
            <TextField
              id="dataSummary"
              type="textarea"
              placeholder=""
              value={dataSummary}
              label="Data Summary"
              onKeyup={(text: string) => setDataSummary(text)}
              feedback=""
            />
          </FormField>
        </FormRow>
      </Form>
      <FormSummary>
        <FormSummaryTitle>Study Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            <b>Name:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br /><br />
            <b>Team Email:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{email}
            <br /><br />
            <b>Acronym:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{acronym}
            <br /><br />
            <b>Ditti ID:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{dittiId}
            <br /><br />
            <b>Default Expiry Delta (days):</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{defaultExpiryDelta}
            <br /><br />
            <b>Is QI:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{isQi ? "Yes" : "No"}
            <br /><br />
            <b>Consent Information:</b><br />
            <div ref={consentPreviewRef} className="ml-4" />
            <br />
            <b>Data Summary:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{dataSummary}
            <br />
          </FormSummaryText>
          <FormSummaryButton onClick={post} disabled={loading}>
            {buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};

export default StudiesEdit;
