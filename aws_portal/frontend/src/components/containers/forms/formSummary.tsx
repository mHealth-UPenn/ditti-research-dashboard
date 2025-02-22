/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { PropsWithChildren } from "react";


const FormSummary = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col flex-shrink-0 px-16 py-12 w-full lg:px-8 lg:w-[20rem] 2xl:w-[28rem] bg-secondary text-white lg:max-h-[calc(100vh-8rem)]">
      {children}
    </div>
  );
};


export default FormSummary;
