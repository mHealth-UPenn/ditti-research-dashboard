import * as React from "react";
import "./checkField.css";

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
    <div>
      {label ? (
        <label className="mr-4" htmlFor={id}>
          {label}
        </label>
      ) : null}
      <input
        type="checkbox"
        checked={prefill}
        onChange={
          onChange
            ? (e) => onChange((e.target as HTMLInputElement).checked)
            : () => null
        }
      />
    </div>
  );
};

export default CheckField;
