import { PropsWithChildren } from "react";


const ViewContainer = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="bg-extra-light min-h-[calc(calc(100vh-8rem)-1px)] h-[calc(calc(100vh-8rem)-1px)] px-4 py-16 md:px-6 overflow-scroll">
      <div className="flex flex-wrap basis-[content]">
        {children}
      </div>
    </div>
  );
};


export default ViewContainer;
