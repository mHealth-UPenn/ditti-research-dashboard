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
