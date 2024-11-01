import { PropsWithChildren } from "react";

interface CardProps {
  width?: "lg" | "md" | "sm";
}

const widthMap = {
  lg: "w-full lg:px-6",
  md: "w-full lg:w-2/3 lg:px-6",
  sm: "w-full lg:w-1/3 lg:px-6",
}


const Card = ({
  width = "lg",
  children
}: PropsWithChildren<CardProps>) => {
  return (
    <div className={widthMap[width]}>
      <div className="bg-white p-8 lg:shadow-lg w-full">
        {children}
      </div>
    </div>
  );
};


export default Card;
