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

import { useState, useEffect } from "react";
import { TextField } from "../fields/textField";
import { AboutSleepTemplate, ResponseBody } from "../../types/api";
import { httpClient } from "../../lib/http";
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
import { useApiHandler } from "../../hooks/useApiHandler";
import { MemoizedQuillField as QuillField } from "../fields/quillField";

/**
 * Component for creating or editing About Sleep templates.
 * Handles fetching template data (for editing) and submitting changes.
 */
export const AboutSleepTemplatesEdit = () => {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  // Determine if editing (ID exists) or creating (ID is 0)
  const aboutSleepTemplateId = id ? parseInt(id) : 0;

  const [name, setName] = useState<string>("");
  const [text, setText] = useState<string>("");

  const { flashMessage } = useFlashMessages();
  const navigate = useNavigate();

  const { safeRequest: safeFetchInitialData, isLoading: isLoadingData } =
    useApiHandler<{
      template: AboutSleepTemplate | null;
    }>({
      showDefaultSuccessMessage: false, // No success message needed for load
    });

  const { safeRequest: safeSubmit } = useApiHandler<ResponseBody>({
    successMessage: (data) => data.msg,
    errorMessage: (error) => `Failed to save template: ${error.message}`,
    onSuccess: () => {
      navigate(-1);
    },
  });

  // Fetch template data if an ID is present in the URL (edit mode)
  useEffect(() => {
    if (aboutSleepTemplateId) {
      const fetchData = async () => {
        const fetchedData = await safeFetchInitialData(async () => {
          // Fetch the specific template
          const templates = await httpClient.request<AboutSleepTemplate[]>(
            `/admin/about-sleep-template?app=1&id=${String(aboutSleepTemplateId)}`
          );
          if (templates.length > 0) {
            return { template: templates[0] };
          } else {
            // Template not found for ID, throw error to be caught by hook
            throw new Error("Template not found.");
          }
        });

        if (fetchedData?.template) {
          // Set state if fetch was successful and template exists
          setName(fetchedData.template.name);
          setText(fetchedData.template.text);
        } else if (fetchedData === null) {
          // Handle case where fetch failed (error handled by hook)
          // Navigate back as template couldn't be loaded
          flashMessage(
            <span>Template not found or failed to load.</span>,
            "danger"
          );
          navigate(-1);
        }
      };
      void fetchData();
    }
    // No fetch needed if creating (ID is 0)
  }, [aboutSleepTemplateId, safeFetchInitialData, flashMessage, navigate]);

  /**
   * Handles form submission: validates input and sends create/update request.
   * Required to return Promise<void> for AsyncButton.
   */
  const post = async (): Promise<void> => {
    // Basic validation
    if (!name.trim()) {
      flashMessage(<span>Name is required.</span>, "danger");
      return;
    }

    // Prepare data and determine endpoint based on create/edit mode
    const data = { text, name };
    const id = aboutSleepTemplateId;
    const body = {
      app: 1, // Admin Dashboard = 1
      ...(id ? { id: id, edit: data } : { create: data }),
    };

    const url = id
      ? "/admin/about-sleep-template/edit"
      : "/admin/about-sleep-template/create";

    // Execute API call via handler
    await safeSubmit(async () => {
      return httpClient.request<ResponseBody>(url, {
        method: "POST",
        data: body,
      });
    });
  };

  const buttonText = aboutSleepTemplateId ? "Update" : "Create";

  // Show loader only during the initial data fetch in edit mode
  if (aboutSleepTemplateId && isLoadingData) {
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
