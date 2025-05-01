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

import { CheckFieldProps } from "./fields.types";

export const CheckField = ({
  id,
  prefill,
  label,
  onChange,
}: CheckFieldProps) => {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-1 hidden md:flex">&nbsp;</div>
      <div className="flex grow items-center">
        <div>
          {label && (
            <label className="mr-4" htmlFor={id}>
              {label}
            </label>
          )}
          <input
            type="checkbox"
            checked={prefill}
            onChange={
              onChange
                ? (e) => {
                    onChange((e.target as HTMLInputElement).checked);
                  }
                : () => null
            }
          />
        </div>
      </div>
    </div>
  );
};
