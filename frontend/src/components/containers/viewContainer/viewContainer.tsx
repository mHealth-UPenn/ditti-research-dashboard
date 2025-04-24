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
import { ViewContainerProps } from "./viewContainer.types";

export const ViewContainer = ({
  navbar = true,
  children,
}: PropsWithChildren<ViewContainerProps>) => {
  const height = navbar
    ? "min-h-[calc(calc(100vh-8rem)-1px)] h-[calc(calc(100vh-8rem)-1px)]"
    : "min-h-[calc(calc(100vh-4rem)-1px)] h-[calc(calc(100vh-4rem)-1px)]";

  return (
    <div
      className={`bg-extra-light ${height} overflow-scroll px-4 py-16 md:px-6`}
    >
      <div className="flex basis-[content] flex-wrap">{children}</div>
    </div>
  );
};
