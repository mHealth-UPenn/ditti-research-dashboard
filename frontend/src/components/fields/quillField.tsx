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

import { debounce } from "lodash";
import { memo, useEffect, useMemo, useRef } from "react";
import Quill, { QuillOptions } from "quill";
import "quill/dist/quill.snow.css";
import { sanitize_quill_html } from "../../utils";
import { QuillFieldProps } from "./fields.types";

const QuillField = ({
  value,
  onChange,
  label,
  description,
  placeholder = "",
  id,
  config = {},
  className = "",
  containerClassName = "",
  readOnly = false,
}: QuillFieldProps) => {
  const editorRef = useRef<HTMLDivElement | null>(null);
  const quillInstanceRef = useRef<Quill | null>(null);

  /**
   * Combine default toolbar configuration with user-provided modules
   * Memoizing this prevents recalculations unless `config.modules` changes.
   */
  const mergedModules = useMemo(() => {
    const defaultModules = {
      toolbar: [
        ["bold", "italic", "underline", "strike"], // Text formatting
        ["link", "blockquote", "code-block"], // Media and block formatting
        [{ list: "ordered" }, { list: "bullet" }], // Lists
        [{ header: [1, 2, 3, 4, 5, 6, false] }], // Headers
        ["clean"], // Clear formatting
      ],
    };
    return {
      ...defaultModules,
      ...(config.modules || {}),
    };
  }, [config.modules]);

  const quillConfig: QuillOptions = useMemo(() => {
    return {
      theme: "snow",
      placeholder,
      readOnly,
      modules: mergedModules,
      ...config,
    };
  }, [placeholder, readOnly, mergedModules, config]);

  /**
   * Debounce the `onChange` handler to limit the frequency of updates
   * during rapid typing, improving performance.
   */
  const debouncedOnChange = useMemo(() => debounce(onChange, 100), [onChange]);

  useEffect(() => {
    if (editorRef.current && !quillInstanceRef.current) {
      // Create a new Quill instance with the computed configuration
      quillInstanceRef.current = new Quill(editorRef.current, quillConfig);

      // Apply custom container class if provided
      if (containerClassName) {
        quillInstanceRef.current.container.classList.add(containerClassName);
      }

      // Listen for editor content changes and call the debounced `onChange`
      quillInstanceRef.current.on("text-change", () => {
        const html = quillInstanceRef.current?.root.innerHTML || "";
        debouncedOnChange(html);
      });

      // Set initial content in the editor, sanitizing it for safety
      if (value) {
        const safeHtml = sanitize_quill_html(value);
        quillInstanceRef.current.clipboard.dangerouslyPasteHTML(safeHtml);
      }
    }

    return () => {
      debouncedOnChange.cancel();
    };
    // Removed 'value' from dependencies to prevent re-running on every value change
  }, [quillConfig, containerClassName, debouncedOnChange]);

  /**
   * Dynamically toggle the editor's `readOnly` state when the prop changes.
   */
  useEffect(() => {
    if (quillInstanceRef.current) {
      quillInstanceRef.current.enable(!readOnly);
    }
  }, [readOnly]);

  return (
    <div className={`mb-4 w-full ${className}`}>
      {/* Display the optional label, if provided */}
      {label && (
        <label htmlFor={id} className="text-gray-700 mb-2 block font-semibold">
          {label}
        </label>
      )}

      {/* Display the optional description, if provided */}
      {description && (
        <p className="text-gray-500 mb-2 text-sm">{description}</p>
      )}

      {/* The container where the Quill editor is mounted */}
      <div>
        <div
          ref={editorRef}
          id={id}
          className="border-gray-300 focus:ring-blue-500 min-h-[10rem] w-full
            rounded-b border p-2 focus:outline-none focus:ring-2"
        />
      </div>
    </div>
  );
};

export const MemoizedQuillField = memo(QuillField);
