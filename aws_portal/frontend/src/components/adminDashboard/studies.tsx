import * as React from "react";
import { Component } from "react";
import Table from "../table/table";
import Navbar from "./navbar";

const data = [
  {
    acronym: "MSBI",
    name: "Multicomponent Behavioral Intervention for Insomnia (MBSI-I) in Older Adults with Mild Cognitive Impairment (ActRelaxed)",
    dittiID: "mb",
    email: "mhealth@pennmedicine.upenn.edu"
  },
  {
    acronym: "MSBI",
    name: "Multicomponent Behavioral Intervention for Insomnia (MBSI-I) in Older Adults with Mild Cognitive Impairment (ActRelaxed)",
    dittiID: "mb",
    email: "mhealth@pennmedicine.upenn.edu"
  },
  {
    acronym: "MSBI",
    name: "Multicomponent Behavioral Intervention for Insomnia (MBSI-I) in Older Adults with Mild Cognitive Impairment (ActRelaxed)",
    dittiID: "mb",
    email: "mhealth@pennmedicine.upenn.edu"
  },
  {
    acronym: "MSBI",
    name: "Multicomponent Behavioral Intervention for Insomnia (MBSI-I) in Older Adults with Mild Cognitive Impairment (ActRelaxed)",
    dittiID: "mb",
    email: "mhealth@pennmedicine.upenn.edu"
  },
  {
    acronym: "MSBI",
    name: "Multicomponent Behavioral Intervention for Insomnia (MBSI-I) in Older Adults with Mild Cognitive Impairment (ActRelaxed)",
    dittiID: "mb",
    email: "mhealth@pennmedicine.upenn.edu"
  },
  {
    acronym: "MSBI",
    name: "Multicomponent Behavioral Intervention for Insomnia (MBSI-I) in Older Adults with Mild Cognitive Impairment (ActRelaxed)",
    dittiID: "mb",
    email: "mhealth@pennmedicine.upenn.edu"
  }
];

interface StudiesProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface StudiesState {
  columns: {
    name: string;
    sortable: boolean;
    width: number;
  }[];
}

class Studies extends React.Component<StudiesProps, StudiesState> {
  state = {
    columns: [
      {
        name: "Acronym",
        searchable: true,
        sortable: true,
        width: 10
      },
      {
        name: "Name",
        searchable: true,
        sortable: true,
        width: 45
      },
      {
        name: "Ditti ID",
        searchable: true,
        sortable: true,
        width: 10
      },
      {
        name: "Email",
        searchable: true,
        sortable: true,
        width: 25
      },
      {
        name: "",
        searchable: false,
        sortable: false,
        width: 10
      }
    ]
  };

  getData = () => {
    return data.map((row) => {
      const { acronym, dittiID, email, name } = row;

      return [
        {
          contents: (
            <div className="flex-center table-data">
              <span>{acronym}</span>
            </div>
          ),
          searchValue: acronym,
          sortValue: acronym
        },
        {
          contents: (
            <div className="flex-center table-data">
              <span>{name}</span>
            </div>
          ),
          searchValue: name,
          sortValue: name
        },
        {
          contents: (
            <div className="flex-center table-data">
              <span>{dittiID}</span>
            </div>
          ),
          searchValue: dittiID,
          sortValue: dittiID
        },
        {
          contents: (
            <div className="flex-center table-data">
              <span>{email}</span>
            </div>
          ),
          searchValue: email,
          sortValue: email
        },
        {
          contents: (
            <div className="flex-center table-control">
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
        <Navbar handleClick={handleClick} active="Studies" />
        <div className="page-content bg-white">
          <Table
            columns={columns}
            control={
              <button className="button-primary">
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

export default Studies;
