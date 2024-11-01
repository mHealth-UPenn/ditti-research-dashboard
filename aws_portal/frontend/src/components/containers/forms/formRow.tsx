import { PropsWithChildren } from "react";


const FormRow = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col md:flex-row">
      {children}
    </div>
  );
};


export default FormRow;
