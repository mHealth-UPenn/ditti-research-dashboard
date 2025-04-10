import { QuillOptions } from "quill";

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
