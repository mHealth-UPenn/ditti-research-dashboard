import { FC, memo } from "react";
import sanitize from "sanitize-html";
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
          className="relative w-full sm:max-w-md m-4 bg-white rounded-xl shadow-lg flex flex-col max-h-[90vh]"
        >
          {/* Modal header */}
          <div className="flex items-center justify-between p-4">
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
            className="p-4 overflow-auto text-black"
            dangerouslySetInnerHTML={{ __html: sanitize(contentHtml) }}
          />

          {/* Modal footer */}
          <div className="p-4 flex items-center justify-end space-x-3 rtl:space-x-reverse">
            <Button onClick={onAccept} rounded size="sm" variant="successDark">
              Accept
            </Button>
            <Button onClick={onDeny} rounded size="sm" variant="dangerDark">
              Deny
            </Button>
          </div>
        </div>
      </div>
    );
  }
);

export default ConsentModal;
