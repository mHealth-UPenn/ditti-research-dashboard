/**
 * Defines the authentication context structure.
 * @property isParticipantAuthenticated - Indicates if the user is authenticated as a participant.
 * @property isResearcherAuthenticated - Indicates if the user is authenticated as a researcher.
 * @property isParticipantLoading - Indicates if the participant authentication status is being checked.
 * @property isResearcherLoading - Indicates if the researcher authentication status is being checked.
 * @property isFirstLogin - Indicates if this is the user's first login session.
 * @property dittiId - The Ditti ID of the authenticated participant.
 * @property accountInfo - Information about the authenticated researcher.
 * @property participantLogin - Function to log in with participant authentication.
 * @property participantLogout - Function to log out from participant authentication.
 * @property researcherLogin - Function to log in with researcher authentication.
 * @property researcherLogout - Function to log out from researcher authentication.
 * @property setIsFirstLogin - Sets whether this is the user's first login session.
 */
export interface AuthContextValue {
  isParticipantAuthenticated: boolean;
  isResearcherAuthenticated: boolean;
  isParticipantLoading: boolean;
  isResearcherLoading: boolean;
  isFirstLogin: boolean;
  dittiId: string | null;
  accountInfo: {
    msg: string;
    email: string;
    firstName: string;
    lastName: string;
    accountId: string;
    phoneNumber?: string;
  };
  participantLogin: (options?: { elevated: boolean }) => void;
  participantLogout: () => void;
  researcherLogin: (options?: { elevated: boolean }) => void;
  researcherLogout: () => void;
  setIsFirstLogin: React.Dispatch<React.SetStateAction<boolean>>;
}
