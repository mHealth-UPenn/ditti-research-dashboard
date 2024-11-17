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
  containerRef: React.RefObject<HTMLDivElement>;
  closeRef: React.RefObject<HTMLDivElement>;
}


const FlashMessage: React.FC<PropsWithChildren<FlashMessageProps>> = ({
  variant,
  containerRef,
  closeRef,
  children,
}) => {
  return (
    <div
      className={`flex justify-between shadow-lg rounded-lg opacity-100 transition-all duration-[2s] z-50 select-none ${variantsBgMap[variant]} ${variantsTextMap[variant]}`}
      ref={containerRef}>
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
