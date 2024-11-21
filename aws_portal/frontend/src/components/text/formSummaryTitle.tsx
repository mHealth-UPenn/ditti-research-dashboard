import { PropsWithChildren } from "react";


const FormSummaryTitle = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <p className="pb-2 mb-8 border-b border-solid border-white text-xl font-bold">{children}</p>
  );
};


export default FormSummaryTitle;
