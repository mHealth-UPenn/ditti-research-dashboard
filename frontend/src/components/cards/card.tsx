import { PropsWithChildren } from "react";
import { CardProps } from "./cards.types";

const widthMap = {
  lg: "w-full lg:px-6",
  md: "w-full md:px-6 lg:w-2/3",
  sm: "w-full md:px-6 md:w-1/2 lg:w-1/3",
};

export const Card = ({
  width = "lg",
  className = "",
  onClick,
  children,
}: PropsWithChildren<CardProps>) => {
  return (
    <div className={widthMap[width]}>
      <div
        className={`mb-8 w-full overflow-x-scroll rounded-xl bg-white p-8
          shadow-lg lg:mb-0 ${className}`}
        onClick={onClick}
      >
        {children}
      </div>
    </div>
  );
};
