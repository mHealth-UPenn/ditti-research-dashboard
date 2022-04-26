import * as React from "react";
import { Component } from "react";
import { ReactComponent as Ascending } from "../../icons/sortAscending.svg";
import { ReactComponent as Descending } from "../../icons/sortDescending.svg";

interface TableHeaderProps {
  columns: {
    ascending: boolean;
    descending: boolean;
    name: string;
    sortable: boolean;
    width: number;
  }[];
  onSort: (name: string, ascending: boolean) => void;
  sortDefault: string;
}

// interface TableHeaderState {}

class TableHeader extends React.Component<TableHeaderProps, any> {
  render() {
    const { columns, onSort, sortDefault } = this.props;

    return (
      <tr>
        {columns.map((c) => (
          <th className="border-light-r" style={{ width: c.width + "%" }}>
            <div>
              <span>{c.name}</span>
              {c.sortable ? (
                <div className="sort">
                  <div
                    className={c.descending ? " sort-active" : ""}
                    onClick={() => onSort(c.name, false)}
                  >
                    <Descending />
                  </div>
                  <div
                    className={c.ascending ? " sort-active" : ""}
                    onClick={() => onSort(c.name, true)}
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
