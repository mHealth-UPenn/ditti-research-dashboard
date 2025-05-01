import { PropsWithChildren } from "react";

export const Form = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="grow bg-white p-12 text-black lg:overflow-y-scroll 2xl:px-24"
    >
      {children}
    </div>
  );
};
