import { PropsWithChildren } from "react";


const FormView = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] overflow-scroll overflow-x-hidden bg-dark lg:flex-row">
      {children}
    </div>
  );
};


export default FormView;
