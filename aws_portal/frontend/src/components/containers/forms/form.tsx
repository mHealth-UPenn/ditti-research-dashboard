import { PropsWithChildren } from "react";


export const Form = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="p-12 2xl:px-24 flex-grow bg-white text-black lg:overflow-y-scroll">
      {children}
    </div>
  );
};
