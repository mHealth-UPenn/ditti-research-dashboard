import { PropsWithChildren } from "react";

export const ListContent = ({ children }: PropsWithChildren) => {
  return <div className="grow bg-white px-6 py-12 lg:px-12">{children}</div>;
};
