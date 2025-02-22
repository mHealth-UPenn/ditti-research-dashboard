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

import * as React from "react";

/**
 * id (optional): an optional html id
 * prefill (optional): whether the field is checked
 * label (optional): the field's label text
 * onChange (optional): a callback function when the field is clicked
 */
interface CheckFieldProps {
  id?: string;
  prefill?: boolean;
  label?: string;
  onChange?: (val: boolean) => void;
}

const CheckField: React.FC<CheckFieldProps> = ({ id, prefill, label, onChange }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="hidden md:flex mb-1">&nbsp;</div>
      <div className="flex flex-grow items-center">
        <div>
          {label &&
            <label className="mr-4" htmlFor={id}>
              {label}
            </label>
          }
          <input
            type="checkbox"
            checked={prefill}
            onChange={
              onChange
                ? (e) => onChange((e.target as HTMLInputElement).checked)
                : () => null
            } />
        </div>
      </div>
    </div>
  );
};

export default CheckField;
