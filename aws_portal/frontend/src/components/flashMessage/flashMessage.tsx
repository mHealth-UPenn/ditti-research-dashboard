import React, { PropsWithChildren } from "react";


interface FlashMessageProps {
  variant: string;
  closeRef: React.RefObject<HTMLDivElement>;
}


const FlashMessage: React.FC<PropsWithChildren<FlashMessageProps>> = ({
  variant,
  closeRef,
  children,
}) => {
  return (
    <div
      className={"shadow flash-message flash-message-" + variant}>
        <div className="flash-message-content">
          <span>{children}</span>
        </div>
        <div className="flash-message-close" ref={closeRef}>
          <span>x</span>
        </div>
    </div>
  );
}


export default FlashMessage;
