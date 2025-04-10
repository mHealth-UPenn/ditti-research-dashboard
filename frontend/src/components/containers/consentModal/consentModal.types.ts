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
