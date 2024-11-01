import { PropsWithChildren } from "react";

interface ButtonProps {
  variant?: "primary" | "secondary";
  className?: string;
  onClick?: () => void;
}

const variantMap = {
  primary: "button-primary",
  secondary: "button-secondary",
}


const Button = ({
  variant = "primary",
  className = "",
  onClick,
  children,
}: PropsWithChildren<ButtonProps>) => {
  return (
    <button
      className={`${variantMap[variant]} px-6 py-4 ${className}`}
      onClick={onClick}>
        {children}
    </button>
  );
};


export default Button;
