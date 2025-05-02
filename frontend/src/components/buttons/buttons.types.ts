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
export type ButtonSize = "sm" | "md" | "lg";

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
  onClick?: () => void | Promise<void>;
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
