import { PropsWithChildren } from "react";


const CardTitle = ({ children }: PropsWithChildren<unknown>) => {
  return <span className="text-2xl font-bold">{children}</span>
};


export default CardTitle;
