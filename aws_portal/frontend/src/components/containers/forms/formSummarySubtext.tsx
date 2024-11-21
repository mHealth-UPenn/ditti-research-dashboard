import { PropsWithChildren } from "react";


const FormSummarySubtext = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="mt-6 text-sm">
      <i>{children}</i>
    </div>
  );
};


export default FormSummarySubtext;
