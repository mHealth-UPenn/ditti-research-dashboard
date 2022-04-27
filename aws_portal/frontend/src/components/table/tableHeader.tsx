import * as React from "react";
import { Component } from "react";
import { ReactComponent as Ascending } from "../../icons/sortAscending.svg";
import { ReactComponent as Descending } from "../../icons/sortDescending.svg";

interface TableHeaderProps {
  headers: {
    ascending: boolean;
    descending: boolean;
    name: string;
    sortable: boolean;
    width: number;
  }[];
  onSort: (name: string, ascending: boolean) => void;
}

// interface TableHeaderState {}

class TableHeader extends React.Component<TableHeaderProps, any> {
  render() {
    const { headers, onSort } = this.props;

    return (
      <tr>
        {headers.map((h) => (
          <th className="border-light-r" style={{ width: h.width + "%" }}>
            <div>
              <span>{h.name}</span>
              {h.sortable ? (
                <div className="sort">
                  <div
                    className={h.descending ? " sort-active" : ""}
                    onClick={() => onSort(h.name, false)}
                  >
                    <Descending />
                  </div>
                  <div
                    className={h.ascending ? " sort-active" : ""}
                    onClick={() => onSort(h.name, true)}
                  >
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
