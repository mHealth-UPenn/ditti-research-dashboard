import React, { useEffect, useRef, useMemo, memo } from "react";
import Quill, { QuillOptions } from "quill";
import { debounce } from "lodash";
import sanitizeHtml from "sanitize-html";
import { QuillFieldProps } from "../../interfaces";
import "quill/dist/quill.snow.css";

const QuillField: React.FC<QuillFieldProps> = ({
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
}) => {
  const editorRef = useRef<HTMLDivElement | null>(null);
  const quillInstanceRef = useRef<Quill | null>(null);

  /**
   * Combine default toolbar configuration with user-provided modules
   * 
   * Memoizing this prevents recalculations unless `config.modules` changes.
   */
  const mergedModules = useMemo(() => {
    const defaultModules = {
      toolbar: [
        ["bold", "italic", "underline", "strike"], // Text formatting
        ["link", "blockquote", "code-block"], // Media and block formatting
        [{ list: "ordered" }, { list: "bullet" }], // Lists
        [{ header: [1, 2, 3, false] }], // Headers
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
        const safeHtml = sanitizeHtml(value);
        quillInstanceRef.current.clipboard.dangerouslyPasteHTML(safeHtml);
      }
    }

    return () => {
      debouncedOnChange.cancel();
    };
  }, [quillConfig, containerClassName, debouncedOnChange, value]);

  /**
   * Synchronize external `value` prop changes with the Quill editor content.
   * 
   * - Prevents redundant updates by comparing current and new HTML
   * - Sanitizes the incoming content before injecting it into the editor
   * - Restores cursor position after content updates
   */
  useEffect(() => {
    if (!quillInstanceRef.current) return;

    const currentHtml = quillInstanceRef.current.root.innerHTML;
    const safeHtml = sanitizeHtml(value);

    if (currentHtml !== safeHtml) {
      const selection = quillInstanceRef.current.getSelection();
      quillInstanceRef.current.clipboard.dangerouslyPasteHTML(safeHtml);

      if (selection) {
        quillInstanceRef.current.setSelection(selection);
      }
    }
  }, [value]);

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
        <label
          htmlFor={id}
          className="mb-2 block font-semibold text-gray-700"
        >
          {label}
        </label>
      )}

      {/* Display the optional description, if provided */}
      {description && (
        <p className="text-sm text-gray-500 mb-2">{description}</p>
      )}

      {/* The container where the Quill editor is mounted */}
      <div
        ref={editorRef}
        id={id}
        className="border border-gray-300 rounded p-2 w-full
                   min-h-[10rem] focus:outline-none focus:ring-2
                   focus:ring-blue-500"
      />
    </div>
  );
};

export default memo(QuillField);
