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
