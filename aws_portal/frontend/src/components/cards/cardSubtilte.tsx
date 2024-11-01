import { PropsWithChildren } from "react";


const CardSubtitle = ({ children }: PropsWithChildren<unknown>) => {
  return <span className="font-thin">{children}</span>
};


export default CardSubtitle;
