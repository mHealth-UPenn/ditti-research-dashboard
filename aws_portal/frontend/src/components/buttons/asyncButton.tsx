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

import { PropsWithChildren, useState } from "react";
import { Button, ButtonProps } from "./button";

/**
 * onClick: the function to handle clicks
 * text: the text to display in the button
 * type: the button's type (primary, secondary, etc.)
 */
interface AsyncButtonProps extends ButtonProps {
  onClick: () => Promise<void>;
}


export const AsyncButton = ({
  variant = "primary",
  size = "md",
  disabled = false,
  square = false,
  fullWidth = false,
  fullHeight = false,
  className = "",
  rounded,
  onClick,
  children,
}: PropsWithChildren<AsyncButtonProps>) => {
  const [loading, setLoading] = useState<boolean>(false);

  /**
   * Show the loader, call the onClick function, and hide the loader when the
   * promise is complete
   */
  const handleClick = (): void => {
    setLoading(true);
    onClick().then(() => setLoading(false));
  };

  const sizeMap = {
    sm: "lds-ring-sm",
    md: "lds-ring-md",
    lg: "lds-ring-lg",
  }

  const sizeContainerMap = {
    sm: "left-[calc(50%-10px)]",
    md: "left-[calc(50%-12px)]",
    lg: "left-[calc(50%-14px)]",
  }

  const loader = (
    <div className={`lds-ring ${sizeMap[size]}`}>
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
      disabled={disabled || loading}
      square={square}
      fullWidth={fullWidth}
      fullHeight={fullHeight}
      className={className}
      rounded={rounded}
      onClick={handleClick}>
        <div className="relative h-full w-full">
          <div className={`absolute top-0 ${sizeContainerMap[size]}`}>
            {loading && loader}
          </div>
          <span className={loading ? "opacity-0" : ""}>{children}</span>
        </div>
    </Button>
  );
};
