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
