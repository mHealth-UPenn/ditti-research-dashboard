import { PropsWithChildren } from "react";


const FormSummaryText = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex-grow flex-shrink-0 mb-8 md:w-1/2 lg:w-full lg:overflow-y-scroll lg:max-h-[calc(100%-6rem)] truncate">
      {children}
    </div>
  );
};


export default FormSummaryText;
