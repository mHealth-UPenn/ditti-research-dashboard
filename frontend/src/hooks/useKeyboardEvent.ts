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

import { useEffect } from "react";

/**
 * Custom hook to handle keyboard events.
 * @param key - The key to listen for (e.g., "Enter", "Escape")
 * @param callback - The function to call when the key is pressed
 * @param isEnabled - Whether the event listener should be active
 * @param options - Additional options for the event listener
 */
export const useKeyboardEvent = (
  key: string,
  callback: () => void,
  isEnabled = true,
  options: { preventDefault?: boolean } = {}
): void => {
  useEffect(() => {
    if (!isEnabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === key) {
        if (options.preventDefault) {
          e.preventDefault();
        }
        callback();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [key, callback, isEnabled, options.preventDefault]);
};

/**
 * Convenience hook for handling Enter key login events.
 * @param isEnabled - Whether the login should be enabled
 * @param loginFunction - The function to call when Enter is pressed
 */
export const useEnterKeyLogin = (
  isEnabled: boolean,
  loginFunction: () => void
): void => {
  useKeyboardEvent("Enter", loginFunction, isEnabled, { preventDefault: true });
};
