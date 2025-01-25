import { PropsWithChildren } from "react";


interface LinkComponentProps {
  onClick?: () => void;
  className?: string;
}


const LinkComponent = ({
  onClick,
  className = "",
  children
}: PropsWithChildren<LinkComponentProps>) => {
  return (
    <span
      className={`${className} text-link underline hover:text-link-hover cursor-pointer`}
      onClick={onClick}>
        {children}
    </span>
  );
};


export default LinkComponent;
