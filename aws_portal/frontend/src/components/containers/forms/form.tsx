import { PropsWithChildren } from "react";


const Form = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="p-12 xl:px-24 flex-grow bg-white text-black lg:overflow-y-scroll">
      {children}
    </div>
  );
};


export default Form;
