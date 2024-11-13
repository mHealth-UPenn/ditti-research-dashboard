import { PropsWithChildren } from "react";


const Subtitle = ({ children }: PropsWithChildren<unknown>) => {
  return <span className="font-thin">{children}</span>
};


export default Subtitle;
