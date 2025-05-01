type CardWidth = "lg" | "md" | "sm";

/**
 * The props for the Card component
 * @property width - The width of the card
 * @property className - The class name of the card
 * @property onClick - The function to handle clicks
 */
export interface CardProps {
  width?: CardWidth;
  className?: string;
  onClick?: () => void;
}

/**
 * The props for the CardContentRow component
 * @property className - The class name of the card content row
 */
export interface CardContentRowProps {
  className?: string;
}
