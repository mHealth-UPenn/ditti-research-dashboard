import { Study } from "../types/api";

/**
 * Defines the context containing information about studies.
 * @property studies - The studies fetched from the database.
 * @property studiesLoading - Whether data is being fetched from the database.
 * @property study - The study currently being viewed.
 */
export interface StudiesContextValue {
  studies: Study[];
  studiesLoading: boolean;
  study: Study | null;
}

/**
 * Props for the StudiesProvider component.
 * @property app - The app ID of the studies.
 */
export interface StudiesProviderProps {
  app: 2 | 3; // Ditti App, Wearable Dashboard
}
