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
  app: 2 | 3;  // Ditti App, Wearable Dashboard
}
