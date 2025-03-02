import { PropsWithChildren } from "react";

interface TableCellProps {
  width: number;
  paddingX?: number;
  paddingY?: number;
}


export const TableCell = ({
  width,
  paddingX,
  paddingY,
  children,
}: PropsWithChildren<TableCellProps>) => {
  let padding = "";
  if (paddingX !== undefined) {
    padding += `px-[${paddingX}px]`;
  } else {
    padding += "px-1 lg:px-2";
  }
  if (paddingY !== undefined) {
    padding += ` py-[${paddingX}px]`;
  } else {
    padding += " py-2";
  }

  return (
    <td
      className="border-t border-r border-light h-[inherit] p-0"
      style={{ width: `${width}%` }}>
        <div className={`w-full h-full flex items-center ${padding}`}>
          <div className={`max-w-[500px] truncate ${paddingY !== undefined ? "h-full" : ""} ${paddingX !== undefined ? "w-full" : ""}`}>
            {children}
          </div>
        </div>
    </td>
  );
};
