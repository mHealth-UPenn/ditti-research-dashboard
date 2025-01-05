import { PropsWithChildren } from "react";
import clsx from "clsx";

interface FormRowProps {
  forceRow?: boolean;
  className?: string;
}

const FormRow = ({
  forceRow = false,
  className,
  children,
}: PropsWithChildren<FormRowProps>) => {
  return (
    <div
      className={clsx(
        "flex",
        { "flex-col": !forceRow, "md:flex-row": true },
        className
      )}
    >
      {children}
    </div>
  );
};

export default FormRow;
