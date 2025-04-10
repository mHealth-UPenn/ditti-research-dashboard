import { BreadcrumbModel } from "../types/models";

/**
 * Defines the context containing information about the navbar.
 * @property breadcrumbs - The breadcrumbs to display in the navbar.
 * @property setStudySlug - Function to set the study slug in the breadcrumbs.
 * @property setSidParam - Function to set the SID parameter in the breadcrumbs.
 * @property setDittiIdParam - Function to set the Ditti ID parameter in the breadcrumbs.
 */
export interface NavbarContextValue {
  breadcrumbs: BreadcrumbModel[];
  setStudySlug: (studyCrumb: string) => void;
  setSidParam: (sid: string) => void;
  setDittiIdParam: (dittiId: string) => void;
}
