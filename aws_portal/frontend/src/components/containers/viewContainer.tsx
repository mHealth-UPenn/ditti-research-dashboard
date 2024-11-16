import { PropsWithChildren } from "react";

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
    <div className={`bg-extra-light ${height} px-4 py-16 md:px-6 overflow-scroll`}>
      <div className="flex flex-wrap basis-[content]">
        {children}
      </div>
    </div>
  );
};


export default ViewContainer;
