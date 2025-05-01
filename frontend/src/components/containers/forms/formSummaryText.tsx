import { PropsWithChildren } from "react";

export const FormSummaryText = ({ children }: PropsWithChildren) => {
  return (
    <div
      className="mb-8 shrink-0 grow truncate md:w-1/2 lg:max-h-[calc(100%-6rem)]
        lg:w-full lg:overflow-y-scroll"
    >
      {children}
    </div>
  );
};
