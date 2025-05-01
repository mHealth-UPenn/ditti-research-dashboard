import { PropsWithChildren } from "react";
import { FormRowProps } from "./forms.types";

export const FormRow = ({
  forceRow = false,
  className = "",
  children,
}: PropsWithChildren<FormRowProps>) => {
  const classes = [
    "flex",
    forceRow ? "md:flex-row" : "flex-col md:flex-row",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <div className={classes}>{children}</div>;
};
