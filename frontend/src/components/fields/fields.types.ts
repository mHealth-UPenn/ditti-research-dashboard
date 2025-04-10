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
import { QuillOptions } from "quill";
import { ChangeEvent, RefObject } from "react";

/**
 * Props for the QuillField component.
 * @property value - The value of the field.
 * @property onChange - Function to call when the value changes.
 * @property label - The label of the field.
 * @property description - The description of the field.
 * @property placeholder - The placeholder of the field.
 * @property id - The id of the field.
 * @property config - The configuration of the Quill editor.
 * @property className - The class name of the field.
 * @property containerClassName - The class name of the container of the field.
 * @property readOnly - Whether the field is read only.
 */
export interface QuillFieldProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  description?: string;
  placeholder?: string;
  id?: string;
  config?: QuillOptions;
  className?: string;
  containerClassName?: string;
  readOnly?: boolean;
}

/**
 * Props for the CheckField component.
 * @property id - The id of the field.
 * @property prefill - Whether the field is checked.
 * @property label - The label of the field.
 * @property onChange - A callback function when the field is clicked.
 */
export interface CheckFieldProps {
  id?: string;
  prefill?: boolean;
  label?: string;
  onChange?: (val: boolean) => void;
}

/**
 * Props for the RadioField component.
 * @property id - The id of the field.
 * @property label - The label of the field.
 * @property checked - The checked value of the field.
 * @property values - The values of the field.
 * @property onChange - A callback function when the field is clicked.
 */
export interface RadioFieldProps {
  id?: string;
  label?: string;
  checked?: string;
  values: string[];
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
}

/**
 * Props for the SelectField component.
 * @property id - The id of the field.
 * @property opts - An array of values and labels for each option.
 * @property placeholder - A placeholder for when no option is selected.
 * @property callback - A callback function for when an option is selected.
 * @property getDefault - Get the default string value given the id that was passed.
 */
export interface SelectFieldProps {
  id: number;
  opts: { value: number; label: string }[];
  placeholder: string;
  disabled?: boolean;
  hideBorder?: boolean;
  callback: (selected: number, id: number) => void;
  getDefault?: (id: number) => number;
}

/**
 * Props for the TextField component.
 * @property id - The id of the field.
 * @property type - The type of the field.
 * @property placeholder - The placeholder of the field.
 * @property prefill - The default value of the field.
 * @property value - The value of the field.
 * @property label - The label of the field.
 * @property description - Additional information about the field.
 * @property onKeyup - A callback function on keyup.
 * @property feedback - Feedback when an error is made.
 * @property disabled - Whether to disable the field.
 * @property required - Whether the field is required. If required, display a required asterisk.
 * @property min - Minimum value for number inputs.
 * @property max - Maximum value for number inputs.
 */
export interface TextFieldProps {
  value: string;
  id?: string;
  type?: string;
  placeholder?: string;
  label?: string;
  description?: string;
  onKeyup?: (text: string) => void;
  onKeyDown?: (e: React.KeyboardEvent) => void;
  feedback?: string;
  disabled?: boolean;
  required?: boolean;
  inputRef?: RefObject<HTMLInputElement>;
  textAreaRef?: RefObject<HTMLTextAreaElement>;
  min?: number;
  max?: number;
}
