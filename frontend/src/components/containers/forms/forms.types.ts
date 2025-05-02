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

/**
 * The props for the FormField component
 * @property className - The class name of the form field
 */
export interface FormFieldProps {
  className?: string;
}

/**
 * The props for the FormRow component
 * @property forceRow - Whether to force the row to be a row
 * @property className - The class name of the form row
 */
export interface FormRowProps {
  forceRow?: boolean;
  className?: string;
}

/**
 * The props for the FormSummaryButton component
 * @property disabled - Whether the button is disabled
 * @property onClick - The function to handle clicks
 */
export interface FormSummaryButtonProps {
  disabled?: boolean;
  onClick: () => Promise<void>;
}
