/**
 * The props for the SubjectsContent component.
 * @property {2 | 3} app - The app number (2 for Ditti, 3 for Wearable)
 */
export interface SubjectsContentProps {
  app: 2 | 3;
}

/**
 * The props for the SubjectsEditContent component.
 * @property {"ditti" | "wearable"} app - The app (Ditti or Wearable)
 */
export interface SubjectsEditContentProps {
  app: "ditti" | "wearable";
}
