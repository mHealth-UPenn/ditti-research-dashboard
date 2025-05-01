import { PropsWithChildren } from "react";

export const FormSummary = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="flex w-full shrink-0 flex-col bg-secondary px-16 py-12
        text-white lg:max-h-[calc(100vh-8rem)] lg:w-80 lg:px-8 2xl:w-[28rem]"
    >
      {children}
    </div>
  );
};
