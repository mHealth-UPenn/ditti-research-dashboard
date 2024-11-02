import { PropsWithChildren } from "react";


const ViewContainer = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="bg-[#F0F0F5] flex flex-wrap basis-[content] min-h-[calc(calc(100vh-8rem)-1px)] h-[calc(calc(100vh-8rem)-1px)] overflow-x-hidden px-4 pt-16 md:px-6 overflow-scroll">
      {children}
    </div>
  );
};


export default ViewContainer;
