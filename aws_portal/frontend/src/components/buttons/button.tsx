import { PropsWithChildren } from "react";

interface ButtonProps {
  variant?: "primary" | "secondary" | "info" | "danger" | "success";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  square?: boolean;
  className?: string;
  onClick?: () => void;
}


const Button = ({
  variant = "primary",
  size = "md",
  disabled = false,
  square = false,
  className = "",
  onClick,
  children,
}: PropsWithChildren<ButtonProps>) => {
  const sizeMap = {
    sm: square ? "px-3 py-3" : "px-4 py-3",
    md: square ? "px-4 py-4" : "px-6 py-4",
    lg: square ? "px-5 py-5" : "px-8 py-5",
  }

  const variantMap = {
    primary: "bg-primary text-white [&:hover:not(:disabled)]:bg-primary-hover",
    secondary: "bg-secondary text-white [&:hover:not(:disabled)]:bg-secondary-hover",
    info: "bg-info text-white [&:hover:not(:disabled)]:bg-info-hover",
    danger: "bg-danger text-white [&:hover:not(:disabled)]:bg-danger-hover",
    success: "bg-success text-white [&:hover:not(:disabled)]:bg-success-hover",
  }

  return (
    <button
      disabled={disabled}
      className={`${variantMap[variant]} ${sizeMap[size]} ${disabled && "cursor-not-allowed opacity-50"} font-bold whitespace-nowrap ${className}`}
      onClick={onClick}>
        {children}
    </button>
  );
};


export default Button;
