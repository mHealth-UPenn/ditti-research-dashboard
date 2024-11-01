import { PropsWithChildren } from "react";

interface CardContentRowProps {
  className?: string;
}


const CardContentRow = ({
  className = "",
  children,
}: PropsWithChildren<CardContentRowProps>) => {
  return (
    <div className={`mb-8 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        {children}
      </div>
    </div>
  );
};


export default CardContentRow;
