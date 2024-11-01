import { PropsWithChildren } from "react";


const Title = ({ children }: PropsWithChildren<unknown>) => {
  return <span className="text-2xl font-bold">{children}</span>
};


export default Title;
