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
 * The variant of the button
 */
export type ButtonVariant =
  | "primary"
  | "secondary"
  | "tertiary"
  | "danger"
  | "dangerDark"
  | "success"
  | "successDark";

/**
 * The size of the button
 */
export type ButtonSize =
  | "sm"
  | "md"
  | "lg";

/**
 * The props for the AsyncButton component
 * @property onClick - The function to handle clicks
 */
export interface AsyncButtonProps extends ButtonProps {
  onClick: () => Promise<void>;
}

/**
 * The props for the Button component
 * @property variant - The variant of the button
 * @property size - The size of the button
 * @property disabled - Whether the button is disabled
 * @property square - Whether the button is square
 * @property fullWidth - Whether the button is full width
 * @property fullHeight - Whether the button is full height
 * @property className - The class name of the button
 * @property rounded - Whether the button is rounded
 * @property onClick - The function to handle clicks
 */
export interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  square?: boolean;
  fullWidth?: boolean;
  fullHeight?: boolean;
  className?: string;
  rounded?: boolean;
  onClick?: () => void;
}

/**
 * The props for the ToggleButton component
 * @property id - The id of the item that will be toggled by the button
 * @property active - Whether the toggled item is currently active
 * @property add - Adds the item
 * @property remove - Removes the item
 */
export interface ToggleButtonProps extends ButtonProps {
  id: number;
  active: boolean;
  add: (id: number) => void;
  remove: (id: number) => void;
}
