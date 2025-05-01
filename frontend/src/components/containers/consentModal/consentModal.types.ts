/**
 * Props for the ConsentModal component.
 * @property isOpen - Whether the modal is open.
 * @property onAccept - Function to call when the user accepts the consent.
 * @property onDeny - Function to call when the user denies the consent.
 * @property onClose - Function to call when the modal is closed.
 * @property contentHtml - The HTML content to display in the modal.
 */
export interface ConsentModalProps {
  isOpen: boolean;
  onAccept: () => void;
  onDeny: () => void;
  onClose: () => void;
  contentHtml: string;
}
