import { PropsWithChildren } from "react";


const FormSummaryButton = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col md:w-1/2 lg:w-full justify-end">
      {children}
    </div>
  );
};


export default FormSummaryButton;
