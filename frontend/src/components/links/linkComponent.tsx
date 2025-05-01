import { PropsWithChildren } from "react";
import { LinkComponentProps } from "./linkComponent.types";

export const LinkComponent = ({
  onClick,
  className = "",
  children,
}: PropsWithChildren<LinkComponentProps>) => {
  return (
    <span
      className={`${className} cursor-pointer text-link underline
        hover:text-link-hover`}
      onClick={onClick}
    >
      {children}
    </span>
  );
};
