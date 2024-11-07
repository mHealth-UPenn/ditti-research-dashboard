import React, { useState, useEffect, createRef } from "react";
import TextField from "../fields/textField";
import {
  AboutSleepTemplate,
  ResponseBody,
  Study,
  ViewProps
} from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import AsyncButton from "../buttons/asyncButton";
import FormView from "../containers/forms/formView";
import Form from "../containers/forms/form";
import FormTitle from "../text/formTitle";
import FormRow from "../containers/forms/formRow";
import FormField from "../containers/forms/formField";
import FormSummary from "../containers/forms/formSummary";
import FormSummaryTitle from "../text/formSummaryTitle";
import FormSummaryContent from "../containers/forms/formSummaryContent";
import FormSummaryText from "../containers/forms/formSummaryText";
import FormSummaryButton from "../containers/forms/formSummaryButton";
import FormSummarySubtext from "../containers/forms/formSummarySubtext";
import sanitize from "sanitize-html";

/**
 * The form's prefill
 */
interface AboutSleepTemplatePrefill {
  name: string;
  text: string;
}

/**
 * aboutSleepTemplateId: the database primary key, 0 if creating a new entry
 */
interface AboutSleepTempaltesEditProps extends ViewProps {
  aboutSleepTemplateId: number;
}

const AboutSleepTempaltesEdit: React.FC<AboutSleepTempaltesEditProps> = ({
  aboutSleepTemplateId,
  goBack,
  flashMessage
}) => {
  const [name, setName] = useState<string>("");
  const [text, setText] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const previewRef = createRef<HTMLDivElement>();

  useEffect(() => {
    if (previewRef.current) {
      previewRef.current.innerHTML = sanitize(text);
    }
  }, [text]);

  useEffect(() => {
    const fetchPrefill = async () => {
      const prefill = await getPrefill();
      setName(prefill.name);
      setText(prefill.text);
      setLoading(false);
    };

    fetchPrefill();
  }, [aboutSleepTemplateId]);

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill = async (): Promise<AboutSleepTemplatePrefill> => {
    const id = aboutSleepTemplateId;

    // if editing an existing entry, return prefill data, else return empty data
    return id
      ? makeRequest("/admin/about-sleep-template?app=1&id=" + id).then(
          makePrefill
        )
      : {
          name: "",
          text: ""
        };
  };

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (res: AboutSleepTemplate[]): AboutSleepTemplatePrefill => {
    const aboutSleepTemplate = res[0];

    return {
      name: aboutSleepTemplate.name,
      text: aboutSleepTemplate.text
    };
  };

  /**
   * POST changes to the backend. Make a request to create an entry if creating
   * a new entry, else make a request to edit an exiting entry
   */
  const post = async (): Promise<void> => {
    const data = { text, name };
    const id = aboutSleepTemplateId;
    const body = {
      app: 1,  // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data })
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id
      ? "/admin/about-sleep-template/edit"
      : "/admin/about-sleep-template/create";

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
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  const buttonText = aboutSleepTemplateId ? "Update" : "Create";

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
        <FormTitle>{aboutSleepTemplateId ? "Edit " : "Create "} Template</FormTitle>
        <FormRow>
          <FormField>
            <TextField
              id="name"
              value={name}
              label="Name"
              onKeyup={setName} />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <TextField
              id="text"
              type="textarea"
              value={text}
              label="Text"
              onKeyup={setText} />
          </FormField>
        </FormRow>
        <div className="px-4">
          <FormTitle>Preview</FormTitle>
        </div>
        <FormRow>
          <div ref={previewRef} className="px-4" />
        </FormRow>
      </Form>
      <FormSummary>
        <FormSummaryTitle>Template Summary</FormSummaryTitle>
        <FormSummaryContent>
          <FormSummaryText>
            Name:
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;{name}
            <br />
          </FormSummaryText>
          <FormSummaryButton>
            <AsyncButton onClick={post}>{buttonText}</AsyncButton>
          </FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};

export default AboutSleepTempaltesEdit;
