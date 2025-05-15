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
