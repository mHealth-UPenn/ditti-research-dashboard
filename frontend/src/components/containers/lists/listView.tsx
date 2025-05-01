import { PropsWithChildren } from "react";

export const ListView = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="flex h-[calc(calc(100vh-8rem)-1px)] w-full flex-col
        overflow-scroll overflow-x-hidden bg-white lg:bg-[transparent] lg:px-12"
    >
      {children}
    </div>
  );
};
