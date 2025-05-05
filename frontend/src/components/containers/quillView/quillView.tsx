/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
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
