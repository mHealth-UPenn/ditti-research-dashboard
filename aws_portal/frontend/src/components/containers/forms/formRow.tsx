import { PropsWithChildren } from "react";

interface FormRowProps {
  forceRow?: boolean;
}


const FormRow = ({
  forceRow = false,
  children
}: PropsWithChildren<FormRowProps>) => {
  return (
    <div className={`flex ${!forceRow && "flex-col"} md:flex-row`}>
      {children}
    </div>
  );
};


export default FormRow;
