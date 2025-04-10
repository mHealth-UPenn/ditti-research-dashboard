import { FlashMessageModel } from "../types/models";

/**
 * The variant of a flash message.
 */
export type FlashMessageVariant = "success" | "info" | "danger";

/**
 * Defines the context containing information about the flash messages.
 * @property flashMessages - The flash messages to display on the page.
 * @property flashMessage - Function to flash a message on the page.
 */
export interface FlashMessageContextValue {
  flashMessages: FlashMessageModel[];
  flashMessage: (msg: React.ReactElement, variant: FlashMessageVariant) => void;
}
