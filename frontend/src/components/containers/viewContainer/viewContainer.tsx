import { PropsWithChildren } from "react";
import { ViewContainerProps } from "./viewContainer.types";

export const ViewContainer = ({
  navbar = true,
  children,
}: PropsWithChildren<ViewContainerProps>) => {
  const height = navbar
    ? "min-h-[calc(calc(100vh-8rem)-1px)] h-[calc(calc(100vh-8rem)-1px)]"
    : "min-h-[calc(calc(100vh-4rem)-1px)] h-[calc(calc(100vh-4rem)-1px)]";

  return (
    <div
      className={`bg-extra-light ${height} overflow-scroll px-4 py-16 md:px-6`}
    >
      <div className="flex basis-[content] flex-wrap">{children}</div>
    </div>
  );
};
