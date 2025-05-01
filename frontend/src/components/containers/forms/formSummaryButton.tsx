import { PropsWithChildren } from "react";
import { AsyncButton } from "../../buttons/asyncButton";
import { FormSummaryButtonProps } from "./forms.types";

export const FormSummaryButton = ({
  disabled,
  onClick,
  children,
}: PropsWithChildren<FormSummaryButtonProps>) => {
  return (
    <div className="flex w-full flex-col justify-end">
      <AsyncButton
        className="p-4"
        onClick={onClick}
        disabled={disabled}
        rounded={true}
      >
        {children}
      </AsyncButton>
    </div>
  );
};
