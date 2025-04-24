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

import React from "react";

/**
 * Represents the response structure from the participant authentication check endpoint.
 * @property msg - A message indicating the status of the login check (e.g., "Login successful").
 * @property dittiId - The Ditti ID of the participant if logged in, otherwise null.
 */
export interface ParticipantAuthResponse {
  msg: string;
  dittiId: string | null;
}

/**
 * Represents the response structure from the researcher authentication check endpoint.
 * @property msg - A message indicating the status of the login check (e.g., "Login successful").
 * @property email - The email address of the researcher.
 * @property firstName - The first name of the researcher.
 * @property lastName - The last name of the researcher.
 * @property accountId - The unique identifier for the researcher's account.
 * @property phoneNumber - The phone number associated with the researcher's account (optional).
 * @property isFirstLogin - Flag indicating if this is the researcher's first login (optional).
 */
export interface ResearcherAuthResponse {
  msg: string;
  email: string;
  firstName: string;
  lastName: string;
  accountId: string;
  phoneNumber?: string;
  isFirstLogin?: boolean;
}

/**
 * Represents the information stored about the currently logged-in researcher account.
 * @property msg - Status message related to the account info retrieval (can be empty if not logged in).
 * @property email - The email address of the researcher.
 * @property firstName - The first name of the researcher.
 * @property lastName - The last name of the researcher.
 * @property accountId - The unique identifier for the researcher's account.
 * @property phoneNumber - The phone number associated with the researcher's account (optional).
 */
export interface ResearcherAccountInfo {
  msg: string;
  email: string;
  firstName: string;
  lastName: string;
  accountId: string;
  phoneNumber?: string;
}

/**
 * Defines the shape of the value provided by the AuthContext.
 * @property isParticipantAuthenticated - True if a participant is currently authenticated, false otherwise.
 * @property isResearcherAuthenticated - True if a researcher is currently authenticated, false otherwise.
 * @property isParticipantLoading - True if the participant authentication status is currently being checked, false otherwise.
 * @property isResearcherLoading - True if the researcher authentication status is currently being checked, false otherwise.
 * @property isFirstLogin - True if the current session is the researcher's first login, false otherwise.
 * @property dittiId - The Ditti ID of the authenticated participant, or null if no participant is authenticated.
 * @property accountInfo - An object containing details about the authenticated researcher's account.
 * @property participantLogin - Function to initiate the participant login flow. Takes optional 'elevated' parameter.
 * @property participantLogout - Function to log out the currently authenticated participant.
 * @property researcherLogin - Function to initiate the researcher login flow. Takes optional 'elevated' parameter.
 * @property researcherLogout - Function to log out the currently authenticated researcher.
 * @property setIsFirstLogin - Function to update the 'isFirstLogin' state, typically used after the first login flow is completed.
 */
export interface AuthContextValue {
  isParticipantAuthenticated: boolean;
  isResearcherAuthenticated: boolean;
  isParticipantLoading: boolean;
  isResearcherLoading: boolean;
  isFirstLogin: boolean;
  dittiId: string | null;
  accountInfo: ResearcherAccountInfo;
  participantLogin: (options?: { elevated: boolean }) => void;
  participantLogout: () => void;
  researcherLogin: (options?: { elevated: boolean }) => void;
  researcherLogout: () => void;
  setIsFirstLogin: React.Dispatch<React.SetStateAction<boolean>>;
}
