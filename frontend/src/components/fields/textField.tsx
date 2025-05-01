import { PropsWithChildren } from "react";
import { TextFieldProps } from "./fields.types";

/**
 * Functional component version of TextField
 */
export const TextField = ({
  id,
  type,
  placeholder,
  label,
  description,
  onKeyup,
  onKeyDown,
  feedback,
  disabled,
  value,
  required = false,
  inputRef,
  textAreaRef,
  min,
  max,
  children,
}: PropsWithChildren<TextFieldProps>) => {
  const handleKeyUp = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    if (onKeyup) {
      onKeyup(e.target.value);
    }
  };

  return (
    <>
      {/* if a label was passed as a prop */}
      {label && (
        <div className="mb-1">
          <label htmlFor={id}>
            {label}
            {required && <span className="ml-1 text-[red]">*</span>}
          </label>
        </div>
      )}

      {/* Render description if provided */}
      {description && (
        <div className="mb-1">
          <small className="text-gray-600">{description}</small>
        </div>
      )}

      <div
        className={`flex items-center ${type === "textarea" ? "h-96" : "h-11"}
          border border-light ${disabled ? "bg-extra-light" : ""}`}
      >
        {/* place children here as prefix icons (e.g., a password icon) */}
        {children ?? null}

        {/* the input */}
        <div className="flex h-full grow items-center p-2">
          {/* textareas require a unique e.target class */}
          {type === "textarea" ? (
            <textarea
              className={`size-full resize-none focus:outline-none ${
                disabled ? "italic text-link" : "" }`}
              onChange={handleKeyUp}
              onKeyDown={onKeyDown}
              disabled={disabled}
              value={value}
              ref={textAreaRef}
            />
          ) : (
            <input
              className={`w-full focus:outline-none ${
                disabled ? "italic text-link" : "" }`}
              type={type ?? "text"}
              placeholder={placeholder ?? ""}
              onChange={handleKeyUp}
              onKeyDown={onKeyDown}
              disabled={disabled}
              value={value}
              {...(type === "number" ? { min, max } : {})} // Pass min and max if type is number
              ref={inputRef}
            />
          )}
        </div>
      </div>

      {/* feedback on error */}
      <span
        className={`text-sm text-[red] ${
          feedback && feedback !== "" ? "" : "hidden" }`}
      >
        {feedback}
      </span>
    </>
  );
};
