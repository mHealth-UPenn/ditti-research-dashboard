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
