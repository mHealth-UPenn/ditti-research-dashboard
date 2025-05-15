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

import { RefObject } from "react";
import { AccountModel } from "../../types/models";

/**
 * Props for the AccountMenu component.
 * @property prefill - The account details to prefill the form with.
 * @property accountMenuRef - The ref object of the account menu.
 * @property hideMenu - The function to call to hide the account menu.
 */
export interface AccountMenuProps {
  prefill: AccountModel;
  accountMenuRef: RefObject<HTMLDivElement>;
  hideMenu: () => void;
}

/**
 * Password error type to handle validation
 */
export type PasswordError =
  | "PASSWORDS_DONT_MATCH"
  | "CURRENT_PASSWORD_REQUIRED"
  | null;
