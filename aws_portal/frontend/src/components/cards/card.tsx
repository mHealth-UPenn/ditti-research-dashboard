import { PropsWithChildren } from "react";

interface CardProps {
  width?: "lg" | "md" | "sm";
}

const widthMap = {
  lg: "w-full",
  md: "w-full lg:w-[calc(65%-8rem)]",
  sm: "w-full lg:w-[calc(32%-8rem)]",
}


const Card = ({
  width = "lg",
  children
}: PropsWithChildren<CardProps>) => {
  return (
    <div className={`bg-white p-8 lg:shadow-lg ${widthMap[width]}`}>
      {children}
    </div>
  );
};


export default Card;
