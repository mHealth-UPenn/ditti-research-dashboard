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
