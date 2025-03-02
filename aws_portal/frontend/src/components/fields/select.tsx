import * as React from "react";
import { useState, useEffect } from "react";

/**
 * id: the value of the selected option
 * opts: an array of values and labels for each option
 * placeholder: a placeholder for when no option is selected
 * callback: a callback function for when an option is selected
 * getDefault: get the default string value given the id that was passed
 */
interface SelectProps {
  id: number;
  opts: { value: number; label: string }[];
  placeholder: string;
  disabled?: boolean;
  hideBorder?: boolean;
  callback: (selected: number, id: number) => void;
  getDefault?: (id: number) => number;
}

export const Select: React.FC<SelectProps> = ({
  id,
  opts,
  placeholder,
  disabled,
  hideBorder = false,
  callback,
  getDefault,
}) => {
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
    <div className={`flex items-center flex-grow relative ${hideBorder ? "" : "border border-light"} ${disabled ? "bg-extra-light" : ""}`}>
      {/* if the blank option is selected, show the placeholder */}
      {value === "0" && (
        <span className="ml-4 text-light pointer-events-none select-none absolute">{placeholder}</span>
      )}
      <select
        className="flex-grow pl-2 bg-[transparent] min-h-[calc(3rem-2px)] focus:outline-none focus:shadow-none cursor-pointer"
        onChange={changeValue}
        value={value}
        disabled={disabled}>
          {updatedOpts.map((opt, i) => (
            <option key={i} value={opt.value}>
              {opt.label}
            </option>
          ))}
      </select>
    </div>
  );
};
