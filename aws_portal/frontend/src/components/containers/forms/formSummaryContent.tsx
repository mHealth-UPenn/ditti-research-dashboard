import { PropsWithChildren } from "react";


export const FormSummaryContent = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col md:flex-row lg:flex-col lg:max-h-[calc(100vh-17rem)] lg:h-full lg:justify-between">
      {children}
    </div>
  );
};
