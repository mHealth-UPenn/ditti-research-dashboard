import { PropsWithChildren } from "react";
import { TableCellProps } from "./table.types";

export const TableCell = ({
  width,
  paddingX,
  paddingY,
  children,
}: PropsWithChildren<TableCellProps>) => {
  let padding = "";
  if (paddingX !== undefined) {
    padding += `px-[${String(paddingX)}px]`;
  } else {
    padding += "px-1 lg:px-2";
  }
  if (paddingY !== undefined) {
    padding += ` py-[${String(paddingY)}px]`;
  } else {
    padding += " py-2";
  }

  return (
    <td
      className="h-[inherit] border-r border-t border-light p-0"
      style={{ width: `${String(width)}%` }}
    >
      <div className={`flex size-full items-center ${padding}`}>
        <div
          className={`max-w-[500px] truncate
            ${paddingY !== undefined ? "h-full" : ""}
            ${paddingX !== undefined ? "w-full" : ""}`}
        >
          {children}
        </div>
      </div>
    </td>
  );
};
