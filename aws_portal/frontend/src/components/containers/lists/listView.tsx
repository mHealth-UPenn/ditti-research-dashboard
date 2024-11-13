import { PropsWithChildren } from "react";


const ListView = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-col bg-white w-full h-[calc(calc(100vh-8rem)-1px)] overflow-x-hidden lg:bg-[transparent] lg:px-12 overflow-y-scroll overflow-x-scroll">
      {children}
    </div>
  );
};


export default ListView;
