import React, { PropsWithChildren, useEffect } from "react";

const variantsBgMap = {
  success: "bg-success-light",
  info: "bg-info-light",
  danger: "bg-danger-light",
};

const variantsTextMap = {
  success: "text-success-dark",
  info: "text-info-dark",
  danger: "text-danger-dark",
};

export type FlashMessageVariant = "success" | "info" | "danger";


/**
 * @property {FlashMessageVariant} variant - The variant of the message (success, info, danger).
 * @property {React.RefObject<HTMLDivElement>} containerRef - A refObject pointing to the container div.
 * @property {Callable} onClose - A function to call when the flash message closes.
 */
interface FlashMessageProps {
  variant: FlashMessageVariant;
  containerRef: React.RefObject<HTMLDivElement>;
  onClose: () => void;
}


const FlashMessage: React.FC<PropsWithChildren<FlashMessageProps>> = ({
  variant,
  containerRef,
  onClose,
  children,
}) => {
  // Set a timeout to fade out the message after 3 seconds
  useEffect(() => {
    const opacityTimeout = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.style.opacity = "0";
      }
    }, 3000);

    const closeTimeout = setTimeout(() => onClose(), 5000);

    return () => {
      clearTimeout(opacityTimeout);
      clearTimeout(closeTimeout);
    };
  }, []);

  return (
    <div
      className={`flex justify-between shadow-lg rounded-lg opacity-100 transition-all duration-[2s] z-50 select-none ${variantsBgMap[variant]} ${variantsTextMap[variant]}`}
      ref={containerRef}>
        <div className="p-4">
          <span>{children}</span>
        </div>
    </div>
  );
}


export default FlashMessage;
