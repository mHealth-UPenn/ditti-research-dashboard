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

import { SleepLog } from "../types/api";

/**
 * Defines the context containing information about wearable data.
 * @property startDate - The start date of the data range.
 * @property endDate - The end date of the data range.
 * @property sleepLogs - The sleep logs for the data range.
 * @property isLoading - Whether data is being fetched from the database.
 * @property isSyncing - Whether data is being synced with the wearable API.
 * @property dataIsUpdated - Whether the current data has been updated since the first load.
 * @property firstDateOfSleep - The first date of sleep data available.
 * @property syncData - Function to invoke a data processing task and sync data with the wearable API.
 * @property decrementStartDate - Function to decrement the start and end dates by one day.
 * @property incrementStartDate - Function to increment the start and end dates by one day.
 * @property resetStartDate - Function to reset the start and end dates.
 * @property canIncrementStartDate - Whether the start date can be incremented.
 */
export interface WearableDataContextValue {
  startDate: Date;
  endDate: Date;
  sleepLogs: SleepLog[];
  isLoading: boolean;
  isSyncing?: boolean;
  dataIsUpdated?: boolean;
  firstDateOfSleep?: Date | null;
  syncData?: () => void;
  decrementStartDate?: () => void;
  incrementStartDate?: () => void;
  resetStartDate?: () => void;
  canIncrementStartDate?: boolean;
}

/**
 * Props for the coordinator wearable data provider.
 * @property dittiId: The Ditti ID of the participant whose data to fetch.
 * @property studyId: The ID of the study to fetch data for.
 */
export interface CoordinatorWearableDataProviderProps {
  dittiId: string;
  studyId: number;
}
