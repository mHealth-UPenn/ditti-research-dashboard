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

import React, { PropsWithChildren, useEffect } from "react";
import { FlashMessageVariant } from "../../contexts/flashMessagesContext.types";

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



/**
 * @property {FlashMessageVariant} variant - The variant of the message (success, info, danger).
 * @property {React.RefObject<HTMLDivElement>} containerRef - A refObject pointing to the container div.
 * @property {Callable} onClose - A function to call when the flash message closes.
 */
interface FlashMessageProps {
  variant: FlashMessageVariant;
  containerRef: React.RefObject<HTMLDivElement>;
  onClose: () => void;
}


export const FlashMessage: React.FC<PropsWithChildren<FlashMessageProps>> = ({
  variant,
  containerRef,
  onClose,
  children,
}) => {
  // Set a timeout to fade out the message after 3 seconds
  useEffect(() => {
    const opacityTimeout = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.style.opacity = "0";
      }
    }, 3000);

    const closeTimeout = setTimeout(() => onClose(), 5000);

    return () => {
      clearTimeout(opacityTimeout);
      clearTimeout(closeTimeout);
    };
  }, []);

  return (
    <div
      className={`flex justify-between shadow-lg rounded-lg opacity-100 transition-all duration-[2s] z-50 select-none ${variantsBgMap[variant]} ${variantsTextMap[variant]}`}
      ref={containerRef}>
        <div className="p-4">
          <span>{children}</span>
        </div>
    </div>
  );
}
