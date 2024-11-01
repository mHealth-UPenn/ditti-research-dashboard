import { PropsWithChildren } from "react";


const FormTitle = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <h1 className="w-full font-bold border-b border-light">{children}</h1>
  );
};


export default FormTitle;
