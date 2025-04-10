/**
 * The variant of a flash message.
 */
export type FlashMessageVariant = "success" | "info" | "danger";

/**
 * @property {FlashMessageVariant} variant - The variant of the message (success, info, danger).
 * @property {React.RefObject<HTMLDivElement>} containerRef - A refObject pointing to the container div.
 * @property {Callable} onClose - A function to call when the flash message closes.
 */
export interface FlashMessageProps {
  variant: FlashMessageVariant;
  containerRef: React.RefObject<HTMLDivElement>;
  onClose: () => void;
}
