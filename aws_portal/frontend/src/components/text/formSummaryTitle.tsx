import { PropsWithChildren } from "react";


const FormSummaryTitle = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <h1 className="border-b border-solid border-white text-xl font-bold">{children}</h1>
  );
};


export default FormSummaryTitle;
