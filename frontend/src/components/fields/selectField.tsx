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
      className={`relative flex grow items-center ${
        hideBorder ? "" : "border border-light" }
        ${disabled ? "bg-extra-light" : ""}`}
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
        className="min-h-[calc(3rem-2px)] grow cursor-pointer bg-[transparent]
          pl-2 focus:shadow-none focus:outline-none"
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
