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
