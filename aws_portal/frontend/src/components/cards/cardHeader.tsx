import { PropsWithChildren } from "react";


const CardHeader = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {children}
      </div>
    </div>
  );
};


export default CardHeader;
