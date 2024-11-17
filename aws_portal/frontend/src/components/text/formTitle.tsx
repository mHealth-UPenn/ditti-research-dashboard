import { PropsWithChildren } from "react";

interface FormTitleProps {
  className?: string;
}


const FormTitle = ({
  children,
  className
}: PropsWithChildren<FormTitleProps>) => {
  return (
    <p className={`text-xl pb-2 mb-8 w-full font-bold border-b border-light ${className}`}>{children}</p>
  );
};


export default FormTitle;
