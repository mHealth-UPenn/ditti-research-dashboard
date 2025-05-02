/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { PropsWithChildren, useState } from "react";
import { Button } from "./button";
import { AsyncButtonProps } from "./buttons.types";

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
   * promise is complete, even if it fails
   */
  const handleClick = (): void => {
    setLoading(true);
    onClick()
      .then(() => {
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      })
      .finally(() => {
        // Ensure loading is reset even if the promise is rejected without being caught
        setLoading(false);
      });
  };

  const sizeMap = {
    sm: "lds-ring-sm",
    md: "lds-ring-md",
    lg: "lds-ring-lg",
  };

  const sizeContainerMap = {
    sm: "left-[calc(50%-10px)]",
    md: "left-[calc(50%-12px)]",
    lg: "left-[calc(50%-14px)]",
  };

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
      onClick={handleClick}
    >
      <div className="relative size-full">
        <div className={`absolute top-0 ${sizeContainerMap[size]}`}>
          {loading && loader}
        </div>
        <span className={loading ? "opacity-0" : ""}>{children}</span>
      </div>
    </Button>
  );
};
