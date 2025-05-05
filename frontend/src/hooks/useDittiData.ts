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

import { useContext } from "react";
import { DittiDataContext } from "../contexts/dittiDataContext";
import { DittiDataContextValue } from "../contexts/dittiDataContext.types";

/**
 * Hook for retrieving context data
 * @returns The current ditti data context.
 */
export const useDittiData = (): DittiDataContextValue => {
  const context = useContext(DittiDataContext);
  if (!context) {
    // Do not throw error and return empty data to accommodate call on participant dashboard.
    return {
      dataLoading: false,
      taps: [],
      audioTaps: [],
      audioFiles: [],
      refreshAudioFiles: () => {
        return Promise.resolve();
      },
    };
  }
  return context;
};
