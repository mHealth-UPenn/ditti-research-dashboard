import React, { useState } from "react";
import "./textField.css";

/**
 * id (optional): an optional html id
 * type (optional): text, number, date, etc.
 * placeholder (optional): an optional placeholder
 * prefill (optional): a default value (which cannot be changed)
 * value (optional): the field's value (which can be changed)
 * label (optional): the field's label
 * onKeyup (optional): a callback function on keyup
 * feedback (optional): feedback when an error is made
 * disabled (optional): whether to disable the field
 */
interface TextFieldProps {
  id?: string;
  type?: string;
  placeholder?: string;
  prefill?: string;
  value?: string;
  label?: string;
  onKeyup?: (text: string) => void;
  feedback?: string;
  disabled?: boolean;
}

/**
 * Functional component version of TextField
 */
const TextField: React.FC<TextFieldProps> = ({
  id,
  type,
  placeholder,
  prefill,
  label,
  onKeyup,
  feedback,
  disabled,
  value,
  children,
}) => {
  const [text, setText] = useState(prefill || "");

  const handleKeyUp = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const inputValue = e.target.value;
    setText(inputValue);
    if (onKeyup) {
      onKeyup(inputValue);
    }
  };

  return (
    <div style={type === "textarea" ? { height: "24rem" } : {}}>
        {/* if a label was passed as a prop */}
        {label &&
          <div className="mb-1">
            <label htmlFor={id}>
              {label}
            </label>
          </div>
        }
        <div className={`flex items-center h-[50px] border border-light ${disabled ? "bg-light" : ""}`}>
          {/* place children here as prefix icons (e.g., a password icon) */}
          {children || null}

          {/* the input */}
          <div className="flex-grow px-2">
            {/* textares require a unique e.target class */}
            {type === "textarea" ? (
              <textarea
                className={`w-full focus:outline-none ${disabled && "italic text-[#666699]"}`}
                defaultValue={prefill ? prefill : undefined}
                onChange={handleKeyUp}
                disabled={disabled} />
            ) : (
              <input
                className={`w-full focus:outline-none ${disabled && "italic text-[#666699]"}`}
                type={type || "text"}
                placeholder={placeholder || ""}
                defaultValue={prefill || undefined}
                value={value ?? text} // Use value if provided, otherwise fall back to internal state
                onChange={handleKeyUp}
                disabled={disabled} />
            )}
          </div>
        </div>

        {/* feedback on error */}
        <span
          className={`text-sm text-[red] ${feedback && feedback !== "" ? "" : "hidden"}`}>
            {feedback}
        </span>
    </div>
  );
};

export default TextField;
