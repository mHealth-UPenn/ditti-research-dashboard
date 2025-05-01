import { PropsWithChildren } from "react";
import { CardContentRowProps } from "./cards.types";

export const CardContentRow = ({
  className = "",
  children,
}: PropsWithChildren<CardContentRowProps>) => {
  return (
    <div className={`mb-8 ${className}`}>
      <div className="mb-4 flex items-center justify-between">{children}</div>
    </div>
  );
};
