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
