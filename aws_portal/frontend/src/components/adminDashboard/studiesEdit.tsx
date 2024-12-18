import React, { useEffect, useState } from "react";
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

interface StudiesEditProps extends ViewProps {
  studyId: number;
}

const StudiesEdit: React.FC<StudiesEditProps> = ({ studyId, goBack, flashMessage }) => {
  // Separate state hooks for each form field and loading state
  const [name, setName] = useState<string>("");
  const [acronym, setAcronym] = useState<string>("");
  const [dittiId, setDittiId] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Fetch prefill data if editing an existing study
    const fetchPrefill = async () => {
      try {
        const prefillData = await getPrefill();
        setName(prefillData.name);
        setAcronym(prefillData.acronym);
        setDittiId(prefillData.dittiId);
        setEmail(prefillData.email);
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

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<{ name: string; acronym: string; dittiId: string; email: string }> => {
    if (studyId === 0) {
      // Creating a new study, return empty prefill data
      return {
        name: "",
        acronym: "",
        dittiId: "",
        email: "",
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
    };
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an existing entry
   */
  const post = async (): Promise<void> => {
    const data = { acronym, dittiId, email, name };
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
            {/* TODO: use textarea for consent information */}
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
      </Form>
      <FormSummary>
        <FormSummaryTitle>Study Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br />
            <br />
            Team Email:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{email}
            <br />
            <br />
            Acronym:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{acronym}
            <br />
            <br />
            Ditti ID:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{dittiId}
            <br />
          </FormSummaryText>
          <FormSummaryButton onClick={post}>
            {buttonText}
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};

export default StudiesEdit;
