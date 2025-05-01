import { PropsWithChildren } from "react";

export const FormSummarySubtext = ({ children }: PropsWithChildren) => {
  return (
    <div className="mt-6 text-sm">
      <i>{children}</i>
    </div>
  );
};
