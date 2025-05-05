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

import { useState, useEffect, useCallback } from "react";
import { TextField } from "../fields/textField";
import { AboutSleepTemplate, ResponseBody } from "../../types/api";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { FormView } from "../containers/forms/formView";
import { Form } from "../containers/forms/form";
import { FormTitle } from "../text/formTitle";
import { FormRow } from "../containers/forms/formRow";
import { FormField } from "../containers/forms/formField";
import { FormSummary } from "../containers/forms/formSummary";
import { FormSummaryTitle } from "../text/formSummaryTitle";
import { FormSummaryContent } from "../containers/forms/formSummaryContent";
import { FormSummaryText } from "../containers/forms/formSummaryText";
import { FormSummaryButton } from "../containers/forms/formSummaryButton";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { MemoizedQuillField as QuillField } from "../fields/quillField";
import { AboutSleepTemplateFormPrefill } from "./adminDashboard.types";

export const AboutSleepTemplatesEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const aboutSleepTemplateId = id ? parseInt(id) : 0;

  const [name, setName] = useState<string>("");
  const [text, setText] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  /**
   * Get the form prefill if editing
   * @returns - the form prefill data
   */
  const getPrefill =
    useCallback(async (): Promise<AboutSleepTemplateFormPrefill> => {
      const id = aboutSleepTemplateId;

      // if editing an existing entry, return prefill data, else return empty data
      return id
        ? makeRequest(
            `/admin/about-sleep-template?app=1&id=${String(id)}`
          ).then((res: ResponseBody) =>
            makePrefill(res as unknown as AboutSleepTemplate[])
          )
        : {
            name: "",
            text: "",
          };
    }, [aboutSleepTemplateId]);

  useEffect(() => {
    const fetchPrefill = async () => {
      const prefill = await getPrefill();
      setName(prefill.name);
      setText(prefill.text);
      setLoading(false);
    };

    void fetchPrefill();
  }, [getPrefill]);

  /**
   * Map the data returned from the backend to form prefill data
   * @param res - the response body
   * @returns - the form prefill data
   */
  const makePrefill = (
    res: AboutSleepTemplate[]
  ): AboutSleepTemplateFormPrefill => {
    const aboutSleepTemplate = res[0];

    return {
      name: aboutSleepTemplate.name,
      text: aboutSleepTemplate.text,
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
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data }),
    };

    const opts = { method: "POST", body: JSON.stringify(body) };
    const url = id
      ? "/admin/about-sleep-template/edit"
      : "/admin/about-sleep-template/create";

    await makeRequest(url, opts).then(handleSuccess).catch(handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  const handleSuccess = (res: ResponseBody) => {
    // go back to the list view and flash a message
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
        <FormTitle>
          {aboutSleepTemplateId ? "Edit " : "Create "} Template
        </FormTitle>
        <FormRow>
          <FormField>
            <TextField id="name" value={name} label="Name" onKeyup={setName} />
          </FormField>
        </FormRow>
        <FormRow>
          <FormField>
            <QuillField
              id="text"
              containerClassName="ql-container-form"
              label="Text"
              description="This is what the user will see when they view the About Sleep screen on the mobile app."
              value={text}
              onChange={setText}
            />
          </FormField>
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
          <FormSummaryButton onClick={post}>{buttonText}</FormSummaryButton>
        </FormSummaryContent>
      </FormSummary>
    </FormView>
  );
};
