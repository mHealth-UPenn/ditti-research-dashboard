import { PropsWithChildren } from "react";


interface LinkProps {
  onClick?: () => void;
  className?: string;
}


const Link = ({
  onClick,
  className = "",
  children
}: PropsWithChildren<LinkProps>) => {
  return (
    <span
      className={`${className} text-link underline hover:text-link-hover cursor-pointer`}
      onClick={onClick}>
        {children}
    </span>
  );
};


export default Link;
