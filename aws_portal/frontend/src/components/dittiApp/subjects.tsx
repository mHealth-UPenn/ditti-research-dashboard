import * as React from "react";
import { Component } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { makeRequest } from "../../utils";
import { Study, User, UserDetails, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";
import SubjectsEdit from "./subjectsEdit";

interface SubjectsProps extends ViewProps {
  studyDetails: Study;
}

interface SubjectsState {
  users: User[];
  columns: Column[];
  loading: boolean;
}

class Subjects extends React.Component<SubjectsProps, SubjectsState> {
  state = {
    users: [],
    columns: [
      {
        name: "Ditti ID",
        searchable: true,
        sortable: true,
        width: 15
      },
      {
        name: "Expires On",
        searchable: false,
        sortable: true,
        width: 30
      },
      {
        name: "Created On",
        searchable: false,
        sortable: true,
        width: 30
      },
      {
        name: "Tapping Access",
        searchable: false,
        sortable: true,
        width: 15
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

  componentDidMount() {
    makeRequest(
      `/aws/scan?app=2&key=User&query=user_permission_idBEGINS"${this.props.studyDetails.dittiId}"`
    ).then((users: User[]) => this.setState({ users, loading: false }));
  }

  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { id, dittiId, email } = this.props.studyDetails;
    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    };

    return this.state.users.map((u: User) => {
      const { tap_permission, user_permission_id, exp_time, createdAt } = u;

      return [
        {
          contents: (
            <div className="flex-left table-data">
              <span>{user_permission_id}</span>
            </div>
          ),
          searchValue: user_permission_id,
          sortValue: user_permission_id
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {new Date(exp_time).toLocaleDateString("en-US", dateOptions)}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: exp_time
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {new Date(createdAt).toLocaleDateString("en-US", dateOptions)}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: createdAt
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{tap_permission ? "Yes" : "No"}</span>
            </div>
          ),
          searchValue: "",
          sortValue: tap_permission ? "1" : "0"
        },
        {
          contents: (
            <div className="flex-left table-control">
              <button
                className="button-secondary"
                onClick={() =>
                  handleClick(
                    ["Edit", user_permission_id],
                    <SubjectsEdit
                      dittiId={user_permission_id}
                      studyId={id}
                      studyEmail={email}
                      studyPrefix={dittiId}
                      flashMessage={flashMessage}
                      goBack={goBack}
                      handleClick={handleClick}
                    />,
                    false
                  )
                }
              >
                Edit Details
              </button>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  render() {
    const { flashMessage, goBack, handleClick } = this.props;
    const { id, dittiId, email } = this.props.studyDetails;
    const { columns, loading } = this.state;

    const tableControl = (
      <button
        className="button-primary"
        onClick={() =>
          handleClick(
            ["Create"],
            <SubjectsEdit
              dittiId=""
              studyId={id}
              studyEmail={email}
              studyPrefix={dittiId}
              flashMessage={flashMessage}
              goBack={goBack}
              handleClick={handleClick}
            />,
            false
          )
        }
      >
        Create&nbsp;<b>+</b>
      </button>
    );

    return (
      <div className="page-container">
        <div className="page-content bg-white">
          {loading ? (
            <SmallLoader />
          ) : (
            <Table
              columns={columns}
              control={tableControl}
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
    );
  }
}

export default Subjects;
