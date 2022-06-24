import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";
import Table, { TableData } from "../table/table";
import AppsEdit from "./appsEdit";
import { makeRequest } from "../../utils";
import { App } from "../../interfaces";

// const data = [
//   {
//     name: "Ditti App"
//   },
//   {
//     name: "Admin Dashboard"
//   }
// ];

interface AppsProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface AppsState {
  apps: App[];
  columns: {
    name: string;
    sortable: boolean;
    width: number;
  }[];
}

class Apps extends React.Component<AppsProps, AppsState> {
  state = {
    apps: [],
    columns: [
      {
        name: "Name",
        searchable: true,
        sortable: true,
        width: 90
      },
      {
        name: "",
        searchable: false,
        sortable: false,
        width: 10
      }
    ]
  };

  async componentDidMount() {
    const apps: App[] = await makeRequest("/admin/app?app=1");
    this.setState({ apps });
  }

  getData = (): TableData[][] => {
    return this.state.apps.map((a) => {
      const { name } = a;

      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <div className="flex-left table-control">
              <button className="button-secondary">Edit</button>
              <button className="button-danger">Delete</button>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  render() {
    const { handleClick } = this.props;
    const { columns } = this.state;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Apps" />
        <div className="page-content bg-white">
          <Table
            columns={columns}
            control={
              <button
                className="button-primary"
                onClick={() =>
                  handleClick(["Create"], <AppsEdit appId={0} />, false)
                }
              >
                Create&nbsp;<b>+</b>
              </button>
            }
            controlWidth={10}
            data={this.getData()}
            includeControl={true}
            includeSearch={true}
            paginationPer={2}
            sortDefault=""
          />
        </div>
      </div>
    );
  }
}

export default Apps;
