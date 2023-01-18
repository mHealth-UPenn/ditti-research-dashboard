import * as React from "react";
import { Component } from "react";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import { getAccess, makeRequest } from "../../utils";
import {
  Study,
  TapDetails,
  User,
  UserDetails,
  ViewProps
} from "../../interfaces";
import { SmallLoader } from "../loader";
import SubjectsEdit from "./subjectsEdit";
import SubjectVisuals from "./subjectVisuals";

/**
 * studyDetails: the details of the study that subjects will be listed for
 * getTaps: get tap data
 */
interface SubjectsProps extends ViewProps {
  studyDetails: Study;
  getTaps: () => TapDetails[];
}

/**
 * canCreate: whether the current user can enroll subjects
 * canEdit: whether the current user can edit subjects
 * users: the rows of the subjects table
 * columns: the columns of the subjects table
 * loading: whether to show the loader
 */
interface SubjectsState {
  canCreate: boolean;
  canEdit: boolean;
  users: User[];
  columns: Column[];
  loading: boolean;
}

class Subjects extends React.Component<SubjectsProps, SubjectsState> {
  state = {
    canCreate: false,
    canEdit: false,
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
    const { dittiId, id } = this.props.studyDetails;

    // get whether the user can enroll subjects
    const create = getAccess(2, "Create", "Users", id)
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    // get whether the user can edit subjects
    const edit = getAccess(2, "Edit", "Users", id)
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    // get all of the study's users
    const url = `/aws/scan?app=2&key=User&query=user_permission_idBEGINS"${dittiId}"`;
    const users = makeRequest(url).then((users: User[]) =>
      this.setState({ users })
    );

    // when all promises complete, hide the loader
    Promise.all([create, edit, users]).then(() =>
      this.setState({ loading: false })
    );
  }

  /**
   * Get the data for the subjects table
   * @returns - The table's contents, consisting of rows of table cells
   */
  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick, getTaps } = this.props;
    const { id, dittiId, email } = this.props.studyDetails;
    const { canEdit, users } = this.state;
    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    };

    return users.map((u: User) => {
      const {
        tap_permission,
        user_permission_id,
        exp_time,
        createdAt,
        information,
        team_email
      } = u;

      const user: UserDetails = {
        tapPermission: tap_permission,
        userPermissionId: user_permission_id,
        expTime: exp_time,
        createdAt: createdAt,
        information: information,
        teamEmail: team_email
      };

      return [
        {
          contents: (
            <div className="flex-left table-data">

              {/* if the user has tap permission, link to a subject visuals page */}
              {u.tap_permission ? (
                <span
                  className="link"
                  onClick={() =>
                    handleClick(
                      [user_permission_id],
                      <SubjectVisuals
                        flashMessage={flashMessage}
                        getTaps={getTaps}
                        goBack={goBack}
                        handleClick={handleClick}
                        studyDetails={this.props.studyDetails}
                        user={user}
                      />
                    )
                  }
                >
                  {user_permission_id}
                </span>
              ) : (
                user_permission_id
              )}
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

              {/* if the user can edit, link to the edit subject page */}
              {canEdit ? (
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
                      />
                    )
                  }
                >
                  Edit Details
                </button>
              ) : null}
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
    const { canCreate, columns, loading } = this.state;

    // if the user can enroll subjects, include an enroll button
    const tableControl = canCreate ? (
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
            />
          )
        }
      >
        Create&nbsp;<b>+</b>
      </button>
    ) : (
      <React.Fragment />
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
