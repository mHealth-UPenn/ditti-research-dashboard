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
