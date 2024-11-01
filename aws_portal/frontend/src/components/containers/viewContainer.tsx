import { PropsWithChildren } from "react";


const ViewContainer = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex flex-wrap bg-white h-[calc(calc(100vh-8rem)-1px)] overflow-x-hidden lg:bg-[transparent] lg:px-6 lg:py-16 overflow-scroll">
      {children}
    </div>
  );
};


export default ViewContainer;
