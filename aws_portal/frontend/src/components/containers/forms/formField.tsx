import { PropsWithChildren } from "react";


const FormField = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex w-full flex-col mb-8">
      {children}
    </div>
  );
};


export default FormField;
