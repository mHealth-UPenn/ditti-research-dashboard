import { PropsWithChildren } from "react";

export const FormSummaryContent = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="flex flex-col md:flex-row lg:h-full
        lg:max-h-[calc(100vh-17rem)] lg:flex-col lg:justify-between"
    >
      {children}
    </div>
  );
};
