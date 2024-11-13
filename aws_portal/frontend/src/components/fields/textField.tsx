import React from "react";
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
  value: string;
  id?: string;
  type?: string;
  placeholder?: string;
  label?: string;
  onKeyup?: (text: string) => void;
  onKeyDown?: (e: React.KeyboardEvent) => void;
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
  label,
  onKeyup,
  onKeyDown,
  feedback,
  disabled,
  value,
  children,
}) => {
  const handleKeyUp = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (onKeyup) {
      onKeyup(e.target.value);
    }
  };

  return (
    <>
        {/* if a label was passed as a prop */}
        {label &&
          <div className="mb-1">
            <label htmlFor={id}>
              {label}
            </label>
          </div>
        }
        <div className={`flex items-center ${type === "textarea" ? "h-[24rem]" : "h-[2.75rem]"} border border-light ${disabled ? "bg-light" : ""}`}>
          {/* place children here as prefix icons (e.g., a password icon) */}
          {children || null}

          {/* the input */}
          <div className="flex items-center flex-grow h-full p-2">
            {/* textares require a unique e.target class */}
            {type === "textarea" ? (
              <textarea
                className={`w-full h-full resize-none focus:outline-none ${disabled && "italic text-link"}`}
                onChange={handleKeyUp}
                onKeyDown={onKeyDown}
                disabled={disabled}
                value={value} />
            ) : (
              <input
                className={`w-full focus:outline-none ${disabled && "italic text-link"}`}
                type={type || "text"}
                placeholder={placeholder || ""}
                onChange={handleKeyUp}
                onKeyDown={onKeyDown}
                disabled={disabled}
                value={value} />
            )}
          </div>
        </div>

        {/* feedback on error */}
        <span
          className={`text-sm text-[red] ${feedback && feedback !== "" ? "" : "hidden"}`}>
            {feedback}
        </span>
    </>
  );
};

export default TextField;
