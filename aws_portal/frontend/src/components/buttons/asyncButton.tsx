import * as React from "react";
import { useState } from "react";

/**
 * onClick: the function to handle clicks
 * text: the text to display in the button
 * type: the button's type (primary, secondary, etc.)
 */
interface AsyncButtonProps {
  onClick: () => Promise<any>;
  text: string;
  type: "primary" | "secondary" | "danger";
  className?: string;
  disabled?: boolean;
}

const variantMap = {
  primary: "bg-primary",
  secondary: "bg-secondary",
  danger: "bg-danger",
}


const AsyncButton: React.FC<AsyncButtonProps> = ({
  onClick,
  text,
  type,
  className,
  disabled,
}) => {
  const [loading, setLoading] = useState<boolean>(false);

  /**
   * Show the loader, call the onClick function, and hide the loader when the
   * promise is complete
   */
  const handleClick = (): void => {
    setLoading(true);
    onClick().then(() => setLoading(false));
  };

  const loader = (
    <div className="lds-ring lds-ring-small">
      <div></div>
      <div></div>
      <div></div>
      <div></div>
    </div>
  );

  return (
    <button
      className={`${variantMap[type]} px-6 py-4 ${className}`}
      onClick={handleClick}
      disabled={disabled || false}>
        {loading ? loader : text}
    </button>
  );
};

export default AsyncButton;
