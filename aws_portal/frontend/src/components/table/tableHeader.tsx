import * as React from "react";
import { Component } from "react";
import { ReactComponent as Ascending } from "../../icons/sortAscending.svg";
import { ReactComponent as Descending } from "../../icons/sortDescending.svg";
import { Header } from "./table";

/**
 * headers: the table's headers
 * onSort: callback function when the user sorts
 */
interface TableHeaderProps {
  headers: Header[];
  onSort: (name: string, ascending: boolean) => void;
}

// interface TableHeaderState {}

class TableHeader extends React.Component<TableHeaderProps, any> {
  render() {
    const { headers, onSort } = this.props;

    return (
      <tr>
        {headers.map((h, i) => (
          <th
            key={i}
            className={
              "bg-light border-light-r" + (h.sortable ? " sortable" : "")
            }
            style={{ width: h.width + "%" }}
            onClick={() => {
              return h.sortable && onSort(h.name, h.ascending == 0);
            }}
          >
            <div>
              <span>{h.name}</span>

              {/* sort buttons */}
              {h.sortable ? (
                <div className="sort">
                  <div className={h.ascending == 0 ? "sort-active" : ""}>
                    <Descending />
                  </div>
                  <div className={h.ascending == 1 ? "sort-active" : ""}>
                    <Ascending />
                  </div>
                </div>
              ) : (
                ""
              )}
            </div>
          </th>
        ))}
      </tr>
    );
  }
}

export default TableHeader;
