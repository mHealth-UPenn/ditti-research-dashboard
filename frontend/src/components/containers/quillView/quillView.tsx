import "quill/dist/quill.snow.css";
import { sanitize_quill_html } from "../../../utils";
import { QuillViewProps } from "./quillView.types";

/**
 * Renders HTML content within a Quill editor styled container.
 * Note: This component does not sanitize the input `content`. Ensure the content
 * is sanitized before passing it to this component to prevent XSS vulnerabilities.
 */
export const QuillView = ({
  content,
  className = "",
  style,
}: QuillViewProps) => {
  const htmlContent = { __html: sanitize_quill_html(content) };

  return (
    <div className={`ql-snow ${className}`} style={style}>
      <div className="ql-editor !p-0" dangerouslySetInnerHTML={htmlContent} />
    </div>
  );
};
