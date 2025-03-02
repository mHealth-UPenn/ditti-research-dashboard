import { PropsWithChildren } from "react";

export interface ButtonProps {
  variant?: "primary" | "secondary" | "tertiary" | "danger" | "dangerDark" | "success" | "successDark";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  square?: boolean;
  fullWidth?: boolean;
  fullHeight?: boolean;
  className?: string;
  rounded?: boolean;
  onClick?: () => void;
}


export const Button = ({
  variant = "primary",
  size = "md",
  disabled = false,
  square = false,
  fullWidth = false,
  fullHeight = false,
  className = "",
  rounded,
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
    tertiary: "bg-white text-link border-link border-2 [&:hover:not(:disabled)]:bg-extra-light",
    danger: "bg-danger text-white [&:hover:not(:disabled)]:bg-danger-hover",
    dangerDark: "bg-danger-dark text-white [&:hover:not(:disabled)]:bg-danger",
    success: "bg-success text-white [&:hover:not(:disabled)]:bg-success-hover",
    successDark: "bg-success-dark text-white [&:hover:not(:disabled)]:bg-success",
  }

  const roundedMap = {
    sm: "rounded",
    md: "rounded-lg",
    lg: "rounded-xl",
  }

  return (
    <button
      disabled={disabled}
      className={`flex items-center justify-center ${variantMap[variant]} ${sizeMap[size]} ${rounded ? roundedMap[size] : ""} ${fullWidth ? "w-full" : ""} ${fullHeight ? "h-full" : ""} ${disabled ? "cursor-not-allowed opacity-50" : ""} whitespace-nowrap ${className} select-none transition-colors duration-200`}
      onClick={onClick}>
        {children}
    </button>
  );
};
