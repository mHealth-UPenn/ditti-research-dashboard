import { PropsWithChildren } from "react";
import { TextProps } from "./text.types";

export const Title = ({ children }: PropsWithChildren<TextProps>) => {
  return <span className="text-2xl font-bold">{children}</span>;
};
