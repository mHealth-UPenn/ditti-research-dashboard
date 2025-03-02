import { PropsWithChildren } from "react";


export const Subtitle = ({ children }: PropsWithChildren<unknown>) => {
  return <span className="font-thin">{children}</span>
};
