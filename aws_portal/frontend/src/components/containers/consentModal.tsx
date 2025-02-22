/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { FC, memo } from "react";
import sanitize, { AllowedAttribute } from "sanitize-html";
import Button from "../buttons/button";
import { ConsentModalProps } from "../../interfaces";

const ConsentModal: FC<ConsentModalProps> = memo(
  ({ isOpen, onAccept, onDeny, onClose, contentHtml }) => {
    if (!isOpen) return null;

    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
        aria-labelledby="consent-modal-title"
        role="dialog"
        aria-modal="true"
      >
        {/* Modal container */}
        <div
          className="relative w-full sm:max-w-[70vw] md:max-w-[60vw] lg:max-w-[50vw] xl:max-w-[40vw] m-4 bg-white rounded-xl shadow-lg flex flex-col max-h-[90vh]"
        >
          {/* Modal header */}
          <div className="flex items-center justify-between p-8">
            <h3
              id="consent-modal-title"
              className="m-0 text-xl font-semibold text-black"
            >
              Consent to Participate in Research
            </h3>
            <button
              type="button"
              className="flex items-center text-black bg-transparent hover:bg-extra-light hover:text-secondary-hover rounded-lg text-sm px-2 py-1"
              onClick={onClose}
            >
              <svg
                className="w-4 h-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 14 14"
                aria-hidden="true"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                />
              </svg>
              <span className="ml-1">Close</span>
              <span className="sr-only">Close modal</span>
            </button>
          </div>

          {/* Modal body */}
          <div
            className="overflow-auto text-black text-sm ql-modal ql-editor"
            dangerouslySetInnerHTML={{
              __html: sanitize(
                contentHtml, {
                allowedAttributes: {
                  li: ["data-list", "class"] as AllowedAttribute[],
                },
              })
            }}
            style={{ padding: "0 2rem" }}
          />

          {/* Modal footer */}
          <div className="p-8 flex items-center justify-end space-x-3 rtl:space-x-reverse">
            <Button onClick={onAccept} rounded size="sm" variant="success">
              Accept
            </Button>
            <Button onClick={onDeny} rounded size="sm" variant="danger">
              Deny
            </Button>
          </div>
        </div>
      </div>
    );
  }
);

export default ConsentModal;
