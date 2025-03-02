import { PropsWithChildren } from "react";


export const Title = ({ children }: PropsWithChildren<unknown>) => {
  return <span className="text-2xl font-bold">{children}</span>
};
