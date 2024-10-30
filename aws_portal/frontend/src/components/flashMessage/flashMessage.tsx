import React, { PropsWithChildren } from "react";

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

interface FlashMessageProps {
  variant: FlashMessageVariant;
  closeRef: React.RefObject<HTMLDivElement>;
}


const FlashMessage: React.FC<PropsWithChildren<FlashMessageProps>> = ({
  variant,
  closeRef,
  children,
}) => {
  return (
    <div
      className={`flex justify-between shadow-lg rounded-lg ${variantsBgMap[variant]} ${variantsTextMap[variant]}`}>
        <div className="p-4">
          <span>{children}</span>
        </div>
        <div className="py-4 px-8 hover:text-black cursor-pointer" ref={closeRef}>
          <span>x</span>
        </div>
    </div>
  );
}


export default FlashMessage;
