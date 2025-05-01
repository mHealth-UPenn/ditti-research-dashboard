import { PropsWithChildren } from "react";

export const FormView = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="flex h-[calc(100vh-8rem)] flex-col overflow-scroll bg-white
        lg:flex-row"
    >
      {children}
    </div>
  );
};
