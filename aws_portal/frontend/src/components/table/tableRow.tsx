import * as React from "react";
import TableCell from "./tableCell";

/**
 * data: the row's cells
 */
interface TableRowProps {
  cells: {
    contents: React.ReactElement | string;
    width: number;
    paddingX?: number;
    paddingY?: number;
  }[];
}

const TableRow: React.FC<TableRowProps> = ({ cells }) => {
  return (
    <tr className="h-[3rem]">
      {cells.map((cell, i) =>
        <TableCell
          key={i}
          width={cell.width}
          paddingX={cell.paddingX}
          paddingY={cell.paddingY}>
            {cell.contents}
        </TableCell>
      )}
    </tr>
  );
};

export default TableRow;
