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

import { FC, memo } from "react";
import { Button } from "../../buttons/button";
import { ConsentModalProps } from "./consentModal.types";
import { QuillView } from "../quillView/quillView";

export const ConsentModal: FC<ConsentModalProps> = memo(
  ({ isOpen, onAccept, onDeny, onClose, contentHtml }: ConsentModalProps) => {
    if (!isOpen) return null;

    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center
          bg-black/50"
        aria-labelledby="consent-modal-title"
        role="dialog"
        aria-modal="true"
      >
        {/* Modal container */}
        <div
          className="relative m-4 flex max-h-[90vh] w-full flex-col rounded-xl
            bg-white shadow-lg sm:max-w-[70vw] md:max-w-[60vw] lg:max-w-[50vw]
            xl:max-w-[40vw]"
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
              className="bg-transparent flex items-center rounded-lg px-2 py-1
                text-sm text-black hover:bg-extra-light
                hover:text-secondary-hover"
              onClick={onClose}
            >
              <svg
                className="size-4"
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
          <QuillView
            className="overflow-auto text-sm text-black"
            content={contentHtml}
            style={{ padding: "0 2rem" }}
          />

          {/* Modal footer */}
          <div
            className="flex items-center justify-end space-x-3 p-8
              rtl:space-x-reverse"
          >
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

ConsentModal.displayName = "ConsentModal";
