import { PropsWithChildren } from "react";


const FormView = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] overflow-x-scroll overflow-y-scroll bg-white lg:flex-row">
      {children}
    </div>
  );
};


export default FormView;
