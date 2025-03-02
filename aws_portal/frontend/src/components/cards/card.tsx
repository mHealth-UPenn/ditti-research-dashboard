import { PropsWithChildren } from "react";

interface CardProps {
  width?: "lg" | "md" | "sm";
  className?: string;
  onClick?: () => void;
}

const widthMap = {
  lg: "w-full lg:px-6",
  md: "w-full md:px-6 lg:w-2/3",
  sm: "w-full md:px-6 md:w-1/2 lg:w-1/3",
}


export const Card = ({
  width = "lg",
  className = "",
  onClick,
  children,
}: PropsWithChildren<CardProps>) => {
  return (
    <div className={widthMap[width]}>
      <div
        className={`bg-white p-8 mb-8 lg:mb-0 shadow-lg w-full overflow-x-scroll rounded-xl ${className}`}
        onClick={onClick}>
          {children}
      </div>
    </div>
  );
};
