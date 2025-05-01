import { PropsWithChildren } from "react";
import { TextProps } from "./text.types";

export const FormSummaryTitle = ({
  children,
}: PropsWithChildren<TextProps>) => {
  return (
    <p
      className="mb-8 border-b border-solid border-white pb-2 text-xl font-bold"
    >
      {children}
    </p>
  );
};
