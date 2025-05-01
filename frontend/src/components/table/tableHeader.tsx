import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { TableHeaderProps } from "./table.types";

export const TableHeader = ({ headers, onSort }: TableHeaderProps) => {
  return (
    <tr className="h-12">
      {headers.map((h, i) => (
        <th
          key={i}
          className={`select-none border-r border-light bg-extra-light
          ${h.sortable ? "cursor-pointer" : ""}`}
          style={{ width: `${String(h.width)}%` }}
          onClick={() => {
            if (h.sortable) {
              onSort(h.name, h.ascending ? 0 : 1);
            }
          }}
        >
          <div
            className="items-begin relative mx-1 flex justify-between lg:mx-2"
          >
            <span className="font-regular whitespace-nowrap text-base">
              {h.name}
            </span>

            {/* sort buttons */}
            {h.sortable &&
              (h.ascending === -1 ? (
                <KeyboardArrowUpIcon className="text-light" />
              ) : h.ascending === 0 ? (
                <KeyboardArrowDownIcon />
              ) : (
                <KeyboardArrowUpIcon />
              ))}
          </div>
        </th>
      ))}
    </tr>
  );
};
