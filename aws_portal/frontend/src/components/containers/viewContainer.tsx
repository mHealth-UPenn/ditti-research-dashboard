import { PropsWithChildren } from "react";
import { APP_ENV } from "../../environment";

interface IViewContainerProps {
  navbar?: boolean;
}


const ViewContainer = ({
  navbar = true,
  children
}: PropsWithChildren<IViewContainerProps>) => {
  const height =
    navbar ?
    "min-h-[calc(calc(100vh-8rem)-1px)] h-[calc(calc(100vh-8rem)-1px)]" :
    "min-h-[calc(calc(100vh-4rem)-1px)] h-[calc(calc(100vh-4rem)-1px)]";

  return (
    <div className={`relative bg-extra-light ${height} px-4 py-16 md:px-6 overflow-scroll`}>
      {APP_ENV === "demo" &&
        <div className="absolute top-[16px] flex justify-center w-full">
          <span className="text-sm italic">All data is simulated and for demonstration purposes only.</span>
        </div>
      }
      <div className="flex flex-wrap basis-[content]">
        {children}
      </div>
    </div>
  );
};


export default ViewContainer;
