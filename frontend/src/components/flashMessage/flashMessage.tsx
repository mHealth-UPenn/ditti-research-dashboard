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

import { PropsWithChildren, useEffect } from "react";
import { FlashMessageProps } from "./flashMessage.types";

const variantsBgMap = {
  success: "bg-success-light",
  info: "bg-info-light",
  danger: "bg-danger-light",
};

const variantsTextMap = {
  success: "text-success-dark",
  info: "text-info-dark",
  danger: "text-danger-dark",
};

export const FlashMessage: React.FC<PropsWithChildren<FlashMessageProps>> = ({
  variant,
  containerRef,
  onClose,
  children,
}: PropsWithChildren<FlashMessageProps>) => {
  // Set a timeout to fade out the message after 3 seconds
  useEffect(() => {
    const opacityTimeout = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.style.opacity = "0";
      }
    }, 3000);

    const closeTimeout = setTimeout(() => {
      onClose();
    }, 5000);

    return () => {
      clearTimeout(opacityTimeout);
      clearTimeout(closeTimeout);
    };
  }, [containerRef, onClose]);

  return (
    <div
      className={`z-50 flex select-none justify-between rounded-lg opacity-100
        shadow-lg transition-all duration-[2s] ${variantsBgMap[variant]}
        ${variantsTextMap[variant]}`}
      ref={containerRef}
    >
      <div className="p-4">
        <span>{children}</span>
      </div>
    </div>
  );
};
