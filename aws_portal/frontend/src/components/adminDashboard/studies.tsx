import * as React from "react";
import { Component } from "react";
import { Study } from "../../interfaces";
import { makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import StudiesEdit from "./studiesEdit";
import { SmallLoader } from "../loader";

interface StudiesProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface StudiesState {
  studies: Study[];
  columns: Column[];
  loading: boolean;
}

class Studies extends React.Component<StudiesProps, StudiesState> {
  state = {
    studies: [],
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
    ],
    loading: true
  };

  async componentDidMount() {
    makeRequest("/admin/study?app=1").then((studies) =>
      this.setState({ studies, loading: false })
    );
  }

  getData = (): TableData[][] => {
    return this.state.studies.map((s: Study) => {
      const { acronym, dittiId, email, id, name } = s;

      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{acronym}</span>
            </div>
          ),
          searchValue: acronym,
          sortValue: acronym
        },
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
            <div className="flex-left table-data">
              <span>{dittiId}</span>
            </div>
          ),
          searchValue: dittiId,
          sortValue: dittiId
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{email}</span>
            </div>
          ),
          searchValue: email,
          sortValue: email
        },
        {
          contents: (
            <div className="flex-left table-control">
              <button
                className="button-secondary"
                onClick={() =>
                  this.props.handleClick(
                    ["Edit", name],
                    <StudiesEdit studyId={id} />,
                    false
                  )
                }
              >
                Edit
              </button>
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
    const { columns, loading } = this.state;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Studies" />
        <div className="page-content bg-white">
          <div style={{ position: "relative", height: "100%", width: "100%" }}>
            {loading ? (
              <SmallLoader />
            ) : (
              <Table
                columns={columns}
                control={
                  <button
                    className="button-primary"
                    onClick={() =>
                      handleClick(
                        ["Create"],
                        <StudiesEdit studyId={0} />,
                        false
                      )
                    }
                  >
                    Create&nbsp;<b>+</b>
                  </button>
                }
                controlWidth={10}
                data={this.getData()}
                includeControl={true}
                includeSearch={true}
                paginationPer={10}
                sortDefault=""
              />
            )}
          </div>
        </div>
      </div>
    );
  }
}

export default Studies;
