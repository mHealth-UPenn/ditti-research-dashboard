import React, { useEffect, useState, createRef } from "react";
import TextField from "../fields/textField";
import CheckField from "../fields/checkField";
import QuillField from "../fields/QuillField";
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
  const dataSummaryPreviewRef = createRef<HTMLDivElement>();

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

  // Sanitize and set dataSummary in the preview
  useEffect(() => {
    if (dataSummaryPreviewRef.current && dataSummary !== "") {
      dataSummaryPreviewRef.current.innerHTML = sanitize(dataSummary);
    }
  }, [dataSummary, dataSummaryPreviewRef]);

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
        isQi: false
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
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async (): Promise<void> => {
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
              type="email"
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
              min={0}
              value={defaultExpiryDelta.toString()}
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
        <FormRow className="mb-8">
          <div ref={consentPreviewRef} className="px-4" />
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
        <FormRow className="mb-8">
          <div ref={dataSummaryPreviewRef} className="px-4" />
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
            <b>Default Enrollment Period (days):</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{defaultExpiryDelta}
            <br /><br />
            <b>Is QI:</b><br />
            &nbsp;&nbsp;&nbsp;&nbsp;{isQi ? "Yes" : "No"}
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
