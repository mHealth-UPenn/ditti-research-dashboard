import { PropsWithChildren } from "react";


const AdminContent = ({ children }: PropsWithChildren<unknown>) => {
  return (
    <div className="flex-grow px-6 py-12 lg:px-12 bg-white">
      {children}
    </div>
  );
};


export default AdminContent;
