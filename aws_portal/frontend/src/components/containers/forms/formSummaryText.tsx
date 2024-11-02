import { PropsWithChildren } from "react";


const FormSummaryText = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex-grow flex-shrink-0 mb-8 md:w-1/2 lg:overflow-y-scroll truncate">
      {children}
    </div>
  );
};


export default FormSummaryText;
