import { PropsWithChildren } from "react";


const FormSummaryContent = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col md:flex-row lg:flex-col lg:max-h-[calc(100vh-17rem)] lg:h-full lg:justify-between">
      <div className="flex-grow mb-8 lg:overflow-y-scroll truncate">
        {children}
      </div>
    </div>
  );
};


export default FormSummaryContent;
