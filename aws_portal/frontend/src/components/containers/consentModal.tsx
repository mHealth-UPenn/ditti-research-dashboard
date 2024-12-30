import React from "react";
import Button from "../buttons/button";
import { ConsentModalProps } from "../../interfaces";

const ConsentModal: React.FC<ConsentModalProps> = ({
  isOpen,
  onAccept,
  onDeny,
  onClose,
  contentHtml,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      aria-labelledby="consent-modal-title"
      role="dialog"
      aria-modal="true"
    >
      {/* Modal content container */}
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow dark:bg-gray-800">

        {/* Modal header */}
        <div className="flex items-center justify-between mb-4">
          <h3 id="consent-modal-title" className="text-xl font-semibold text-gray-900 dark:text-white">
            Consent to Participate in Research
          </h3>
          <button
            type="button"
            className="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white"
            onClick={onClose}
          >
            <svg className="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
              <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
            </svg>
            <span className="sr-only">Close modal</span>
          </button>
        </div>
        
        {/* Modal body: raw HTML content */}
        <div
          className="mb-6 text-gray-700 dark:text-gray-200"
          dangerouslySetInnerHTML={{ __html: contentHtml }}
        />

        {/* Modal footer: Accept / Deny / Close */}
        <div className="flex items-center justify-end space-x-3 rtl:space-x-reverse">
          <Button onClick={onAccept} rounded={true} size="sm" variant="success">
            Accept
          </Button>
          <Button onClick={onDeny} rounded={true} size="sm" variant="danger">
            Deny
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ConsentModal;
