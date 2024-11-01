import { PropsWithChildren } from "react";


interface LinkProps {
  onClick?: () => void;
}


const Link = ({ onClick, children }: PropsWithChildren<LinkProps>) => {
  return (
    <span
      className="text-link underline hover:text-link-hover"
      onClick={onClick}>
        {children}
    </span>
  );
};


export default Link;
