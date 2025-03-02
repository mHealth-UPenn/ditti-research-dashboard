import { PropsWithChildren } from "react";


export const FormSummary = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col flex-shrink-0 px-16 py-12 w-full lg:px-8 lg:w-[20rem] 2xl:w-[28rem] bg-secondary text-white lg:max-h-[calc(100vh-8rem)]">
      {children}
    </div>
  );
};
