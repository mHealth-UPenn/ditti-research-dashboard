import * as React from "react";
import { Header } from "./table";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";

/**
 * headers: the table's headers
 * onSort: callback function when the user sorts
 */
interface TableHeaderProps {
  headers: Header[];
  onSort: (name: string, ascending: boolean) => void;
}

const TableHeader: React.FC<TableHeaderProps> = ({ headers, onSort }) => {
  return (
    <tr>
      {headers.map((h, i) => (
        <th
          key={i}
          className={`bg-light border-r border-light select-none ${h.sortable && "cursor-pointer"}`}
          style={{ width: h.width + "%" }}
          onClick={() => {
            return h.sortable && onSort(h.name, h.ascending === 0);
          }}>
            <div className="flex items-begin justify-between mx-1 my-4 relative lg:mx-2">
              <span className="text-base font-regular whitespace-nowrap">{h.name}</span>

              {/* sort buttons */}
              {h.sortable && (
                h.ascending === -1 ?
                <KeyboardArrowUpIcon className={"text-light"} /> :
                <>
                  <KeyboardArrowUpIcon className={h.ascending === 0 ? "" : "invisible"} />
                  <KeyboardArrowDownIcon className={h.ascending === 1 ? "" : "invisible"} />
                </>
              )}
            </div>
        </th>
      ))}
    </tr>
  );
};

export default TableHeader;
