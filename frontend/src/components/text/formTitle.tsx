import { PropsWithChildren } from "react";
import { TextProps } from "./text.types";
export const FormTitle = ({
  children,
  className = "",
}: PropsWithChildren<TextProps>) => {
  return (
    <p
      className={`mb-8 w-full border-b border-light pb-2 text-xl font-bold
        ${className}`}
    >
      {children}
    </p>
  );
};
