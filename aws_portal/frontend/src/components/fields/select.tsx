import * as React from "react";
import { useState, useEffect } from "react";
import "./select.css";

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
  callback: (selected: number, id: number) => void;
  getDefault?: (id: number) => number;
}

const Select: React.FC<SelectProps> = ({
  id,
  opts,
  placeholder,
  disabled,
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
    <div
      style={{
        alignItems: "center",
        display: "flex",
        flexGrow: 1,
        position: "relative",
      }}>
      {/* if the blank option is selected, show the placeholder */}
      {value === "0" && (
        <div className="select-placeholder">{placeholder}</div>
      )}
      <select
        onChange={changeValue}
        value={value}
        style={{ minHeight: "calc(3rem - 2px)" }}
        disabled={disabled}
        className={disabled ? "bg-transparent" : ""}>
        {updatedOpts.map((opt, i) => (
          <option key={i} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Select;
