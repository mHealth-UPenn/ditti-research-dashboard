import { PropsWithChildren } from "react";
import { FormFieldProps } from "./forms.types";

export const FormField = ({
  className,
  children,
}: PropsWithChildren<FormFieldProps>) => {
  return (
    <div className={`mb-8 flex w-full flex-col px-4 ${className ?? ""}`}>
      {children}
    </div>
  );
};
