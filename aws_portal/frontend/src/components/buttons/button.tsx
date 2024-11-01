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
      className={`${variantMap[variant]} button-lg mb-2 ${className}`}
      onClick={onClick}>
        {children}
    </button>
  );
};


export default Button;
