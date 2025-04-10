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
