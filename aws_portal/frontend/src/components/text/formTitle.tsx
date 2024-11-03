import { PropsWithChildren } from "react";


const FormTitle = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <p className="text-xl pb-2 mb-8 w-full font-bold border-b border-light">{children}</p>
  );
};


export default FormTitle;
