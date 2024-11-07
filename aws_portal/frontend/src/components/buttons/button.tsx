import { PropsWithChildren } from "react";

export interface ButtonProps {
  variant?: "primary" | "secondary" | "info" | "danger" | "success";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  square?: boolean;
  fullWidth?: boolean;
  fullHeight?: boolean;
  className?: string;
  title?: string;
  onClick?: () => void;
}


const Button = ({
  variant = "primary",
  size = "md",
  disabled = false,
  square = false,
  fullWidth = false,
  fullHeight = false,
  className = "",
  onClick,
  children,
}: PropsWithChildren<ButtonProps>) => {
  const sizeMap = {
    sm: `text-sm ${square ? `${!fullWidth ? "px-3" : ""} ${!fullHeight ? "py-3" : ""}` : `${!fullWidth ? "px-4" : ""} ${!fullHeight ? "py-3" : ""}`}`,
    md: `text-[1rem] ${square ? `${!fullWidth ? "px-4" : ""} ${!fullHeight ? "py-4" : ""}` : `${!fullWidth ? "px-6" : ""} ${!fullHeight ? "py-4" : ""}`}`,
    lg: `text-lg ${square ? `${!fullWidth ? "px-5" : ""} ${!fullHeight ? "py-5" : ""}` : `${!fullWidth ? "px-8" : ""} ${!fullHeight ? "py-5" : ""}`}`,
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
      className={`flex items-center justify-center ${variantMap[variant]} ${sizeMap[size]} ${fullWidth ? "w-full" : ""} ${fullHeight ? "h-full" : ""} ${disabled ? "cursor-not-allowed opacity-50" : ""} whitespace-nowrap ${className} select-none`}
      onClick={onClick}>
        {children}
    </button>
  );
};


export default Button;
