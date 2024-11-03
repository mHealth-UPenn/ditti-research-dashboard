import * as React from "react";
import { useState } from "react";
import Button, { ButtonProps } from "./button";

/**
 * onClick: the function to handle clicks
 * text: the text to display in the button
 * type: the button's type (primary, secondary, etc.)
 */
interface AsyncButtonProps extends ButtonProps {
  onClick: () => Promise<any>;
}


const AsyncButton: React.FC<AsyncButtonProps> = ({
  variant = "primary",
  size = "md",
  disabled = false,
  square = false,
  fullWidth = false,
  fullHeight = false,
  className = "",
  onClick,
  children,
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
    <Button
      variant={variant}
      size={size}
      disabled={disabled}
      square={square}
      fullWidth={fullWidth}
      fullHeight={fullHeight}
      className={className}
      onClick={handleClick}>
        {children}
    </Button>
  );
};

export default AsyncButton;
