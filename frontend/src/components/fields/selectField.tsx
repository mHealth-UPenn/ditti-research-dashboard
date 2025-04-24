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

import { useState, useEffect } from "react";
import { SelectFieldProps } from "./fields.types";

export const SelectField = ({
  id,
  opts,
  placeholder,
  disabled,
  hideBorder = false,
  callback,
  getDefault,
}: SelectFieldProps) => {
  const [value, setValue] = useState<string>("");

  // set the default value
  useEffect(() => {
    if (getDefault) {
      setValue(String(getDefault(id)));
    }
  }, [getDefault, id]);

  /**
   * Change the displayed value when an option is selected and call the
   * callback function
   * @param e - the select field's change event
   */
  const changeValue = (e: React.ChangeEvent<HTMLSelectElement>): void => {
    const value = e.target.value;
    setValue(value);
    callback(parseInt(value), id);
  };

  // always start with a blank option
  const updatedOpts = [{ value: 0, label: "" }].concat(opts);

  return (
    <div
      className={`relative flex flex-grow items-center ${
        hideBorder
            ? ""
            : "border border-light"
       
        } ${disabled ? "bg-extra-light" : ""}`}
    >
      {/* if the blank option is selected, show the placeholder */}
      {value === "0" && (
        <span
          className="pointer-events-none absolute ml-4 select-none text-light"
        >
          {placeholder}
        </span>
      )}
      <select
        className="min-h-[calc(3rem-2px)] flex-grow cursor-pointer
          bg-[transparent] pl-2 focus:shadow-none focus:outline-none"
        onChange={changeValue}
        value={value}
        disabled={disabled}
      >
        {updatedOpts.map((opt, i) => (
          <option key={i} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};
