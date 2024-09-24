import * as React from "react";
import "./radioField.css";

/**
 * id (optional): an optional html id
 * prefill (optional): whether the field is checked
 * label (optional): the field's label text
 * onChange (optional): a callback function when the field is clicked
 */
interface RadioFieldProps {
  id?: string;
  prefill?: boolean;
  label?: string;
  values: string[];
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const RadioField: React.FC<RadioFieldProps> = ({
    id,
    prefill,
    label,
    values,
    onChange
}) => {
  return (
    <div className="radio-field-container">
      {label && (
        <span className="radio-field-main-label">
          {label}
        </span>
      )}
      {values.map((v, i) =>
        <div className="radio-field-input-container" key={i}>
          <label htmlFor={id} className="radio-field-label">
            {v}
          </label>
          <input
            type="radio"
            // checked={prefill}
            name={id}
            value={v}
            onChange={onChange || (e => null)}
          />
        </div>
      )}
    </div>
  );
};

export default RadioField;
