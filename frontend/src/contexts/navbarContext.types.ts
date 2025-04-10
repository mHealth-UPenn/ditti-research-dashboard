/**
 * Defines the context containing information about the navbar.
 * @property breadcrumbs - The breadcrumbs to display in the navbar.
 * @property setStudySlug - Function to set the study slug in the breadcrumbs.
 * @property setSidParam - Function to set the SID parameter in the breadcrumbs.
 * @property setDittiIdParam - Function to set the Ditti ID parameter in the breadcrumbs.
 */
export interface NavbarContextValue {
  breadcrumbs: Breadcrumb[];
  setStudySlug: (studyCrumb: string) => void;
  setSidParam: (sid: string) => void;
  setDittiIdParam: (dittiId: string) => void;
}

/**
 * Breadcrumbs for display in the Navbar component.
 * @property name - The name of the breadcrumb to display in the navbar.
 * @property link - The link to navigate to when the breadcrumb is clicked.
 */
export interface Breadcrumb {
  name: string;
  link: string | null;
}

/**
 * Handles the breadcrumbs for the Navbar component.
 * @property breadcrumbs - The breadcrumbs to display in the navbar.
 */
export interface Handle {
  breadcrumbs: Breadcrumb[];
}
