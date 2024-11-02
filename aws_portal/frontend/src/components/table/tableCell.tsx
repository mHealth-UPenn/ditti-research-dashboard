import { PropsWithChildren } from "react";

interface TableCellProps {
  width: number;
  paddingX?: number;
  paddingY?: number;
}


const TableCell = ({
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
      className="border-t border-r border-light height-[inherit] p-0"
      style={{ width: `${width}%` }}>
        <div className={`w-full h-full flex items-center truncate ${padding}`}>
          {children}
        </div>
    </td>
  );
};


export default TableCell;
