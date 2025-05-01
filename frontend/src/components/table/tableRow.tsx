import { TableCell } from "./tableCell";
import { TableRowProps } from "./table.types";

export const TableRow = ({ cells }: TableRowProps) => {
  return (
    <tr className="h-12">
      {cells.map((cell, i) => (
        <TableCell
          key={i}
          width={cell.width}
          paddingX={cell.paddingX}
          paddingY={cell.paddingY}
        >
          {cell.contents}
        </TableCell>
      ))}
    </tr>
  );
};
