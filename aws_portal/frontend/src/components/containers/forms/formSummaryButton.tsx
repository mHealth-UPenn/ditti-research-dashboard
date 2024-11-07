import { PropsWithChildren } from "react";


const FormSummaryButton = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col w-full w-full justify-end">
      {children}
    </div>
  );
};


export default FormSummaryButton;
