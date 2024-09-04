import * as React from "react";

/**
 * data: the row's cells
 */
interface TableRowProps {
  data: { contents: React.ReactElement; width: number }[];
}

const TableRow: React.FC<TableRowProps> = ({ data }) => {
  return (
    <tr>
      {data.map((cell, i) => (
        <td
          key={i}
          className="border-light-t border-light-r"
          style={{ width: cell.width + "%" }}
        >
          {cell.contents}
        </td>
      ))}
    </tr>
  );
};

export default TableRow;
