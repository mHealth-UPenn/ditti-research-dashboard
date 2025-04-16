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
