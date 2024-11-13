import { PropsWithChildren } from "react";
import AsyncButton from "../../buttons/asyncButton";

interface FormSummaryButtonProps {
  disabled?: boolean;
  onClick: () => Promise<void>;
}


const FormSummaryButton = ({
  disabled,
  onClick,
  children
}: PropsWithChildren<FormSummaryButtonProps>) => {
  return (
    <div className="flex flex-col w-full w-full justify-end">
      <AsyncButton
        className="p-4"
        onClick={onClick}
        disabled={disabled}
        rounded={true}>
          {children}
      </AsyncButton>
    </div>
  );
};


export default FormSummaryButton;
