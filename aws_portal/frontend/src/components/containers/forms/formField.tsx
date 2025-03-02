import { PropsWithChildren } from "react";

interface FormFieldProps {
  className?: string;
}


export const FormField = ({
  className,
  children
}: PropsWithChildren<FormFieldProps>) => {
  return (
    <div className={`flex w-full flex-col mb-8 px-4 ${className}`}>
      {children}
    </div>
  );
};
