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

import React, { PropsWithChildren, RefObject } from "react";

/**
 * id (optional): an optional html id
 * type (optional): text, number, date, etc.
 * placeholder (optional): an optional placeholder
 * prefill (optional): a default value (which cannot be changed)
 * value (optional): the field's value (which can be changed)
 * label (optional): the field's label
 * description (optional): additional information about the field
 * onKeyup (optional): a callback function on keyup
 * feedback (optional): feedback when an error is made
 * disabled (optional): whether to disable the field
 * required (optional): whether the field is required. If required, display a required asterisk.
 * min (optional): minimum value for number inputs
 * max (optional): maximum value for number inputs
 */
interface TextFieldProps {
  value: string;
  id?: string;
  type?: string;
  placeholder?: string;
  label?: string;
  description?: string;
  onKeyup?: (text: string) => void;
  onKeyDown?: (e: React.KeyboardEvent) => void;
  feedback?: string;
  disabled?: boolean;
  required?: boolean;
  inputRef?: RefObject<HTMLInputElement>;
  textAreaRef?: RefObject<HTMLTextAreaElement>;
  min?: number;
  max?: number;
}

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
            {label}{required && <span className="ml-1 text-[red]">*</span>}
          </label>
        </div>
      }

      {/* Render description if provided */}
      {description && (
        <div className="mb-1">
          <small className="text-gray-600">{description}</small>
        </div>
      )}

      <div
        className={`flex items-center ${
          type === "textarea" ? "h-[24rem]" : "h-[2.75rem]"
        } border border-light ${disabled ? "bg-extra-light" : ""}`}
      >
        {/* place children here as prefix icons (e.g., a password icon) */}
        {children || null}

        {/* the input */}
        <div className="flex items-center flex-grow h-full p-2">
          {/* textareas require a unique e.target class */}
          {type === "textarea" ? (
            <textarea
              className={`w-full h-full resize-none focus:outline-none ${
                disabled && "italic text-link"
              }`}
              onChange={handleKeyUp}
              onKeyDown={onKeyDown}
              disabled={disabled}
              value={value}
              ref={textAreaRef} 
            />
          ) : (
            <input
              className={`w-full focus:outline-none ${
                disabled && "italic text-link"
              }`}
              type={type || "text"}
              placeholder={placeholder || ""}
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
          feedback && feedback !== "" ? "" : "hidden"
        }`}
      >
        {feedback}
      </span>
    </>
  );
};
