import { FlashMessageVariant } from "../components/flashMessage/flashMessage.types";

/**
 * Defines the context containing information about the flash messages.
 * @property flashMessages - The flash messages to display on the page.
 * @property flashMessage - Function to flash a message on the page.
 */
export interface FlashMessageContextValue {
  flashMessages: FlashMessageModel[];
  flashMessage: (msg: React.ReactElement, variant: FlashMessageVariant) => void;
}

/**
 * A flash message to be displayed in the frontend.
 * @property id - The database primary key.
 * @property element - The element to display in the flash message.
 * @property containerRef - The reference to the container element.
 */
export interface FlashMessageModel {
  id: number;
  element: React.ReactElement;
  containerRef: React.RefObject<HTMLDivElement>;
}
