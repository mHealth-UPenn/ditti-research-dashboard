import { PropsWithChildren } from "react";


export const ListContent = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex-grow px-6 py-12 lg:px-12 bg-white">
      {children}
    </div>
  );
};
