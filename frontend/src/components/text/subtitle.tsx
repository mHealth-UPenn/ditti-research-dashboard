import { PropsWithChildren } from "react";
import { TextProps } from "./text.types";

export const Subtitle = ({ children }: PropsWithChildren<TextProps>) => {
  return <span className="font-thin">{children}</span>;
};
