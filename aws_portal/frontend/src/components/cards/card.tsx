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

import { PropsWithChildren } from "react";

interface CardProps {
  width?: "lg" | "md" | "sm";
  className?: string;
  onClick?: () => void;
}

const widthMap = {
  lg: "w-full lg:px-6",
  md: "w-full md:px-6 lg:w-2/3",
  sm: "w-full md:px-6 md:w-1/2 lg:w-1/3",
}


export const Card = ({
  width = "lg",
  className = "",
  onClick,
  children,
}: PropsWithChildren<CardProps>) => {
  return (
    <div className={widthMap[width]}>
      <div
        className={`bg-white p-8 mb-8 lg:mb-0 shadow-lg w-full overflow-x-scroll rounded-xl ${className}`}
        onClick={onClick}>
          {children}
      </div>
    </div>
  );
};
