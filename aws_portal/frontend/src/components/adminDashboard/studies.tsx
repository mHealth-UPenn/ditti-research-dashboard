import * as React from "react";
import { Component } from "react";
import { ResponseBody, Study, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import StudiesEdit from "./studiesEdit";
import { SmallLoader } from "../loader";

interface StudiesState {
  canCreate: boolean;
  canEdit: boolean;
  studies: Study[];
  columns: Column[];
  loading: boolean;
}

class Studies extends React.Component<ViewProps, StudiesState> {
  state = {
    canCreate: false,
    canEdit: false,
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
    const create = getAccess(1, "Create", "Studies")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    const edit = getAccess(1, "Edit", "Studies")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    const studies = makeRequest("/admin/study?app=1").then((studies) =>
      this.setState({ studies })
    );

    Promise.all([create, edit, studies]).then(() =>
      this.setState({ loading: false })
    );
  }

  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, studies } = this.state;

    return studies.map((s: Study) => {
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
              {canEdit ? (
                <button
                  className="button-secondary"
                  onClick={() =>
                    handleClick(
                      ["Edit", name],
                      <StudiesEdit
                        studyId={id}
                        flashMessage={flashMessage}
                        goBack={goBack}
                        handleClick={handleClick}
                      />
                    )
                  }
                >
                  Edit
                </button>
              ) : null}
              <button className="button-danger" onClick={() => this.delete(id)}>
                Delete
              </button>
            </div>
          ),
          searchValue: "",
          sortValue: ""
        }
      ];
    });
  };

  delete = (id: number): void => {
    const body = { app: 1, id };
    const opts = { method: "POST", body: JSON.stringify(body) };
    makeRequest("/admin/study/archive", opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    const { flashMessage } = this.props;
    flashMessage(<span>{res.msg}</span>, "success");
  };

  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    const msg = (
      <span>
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  render() {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canCreate, columns, loading } = this.state;

    const tableControl = canCreate ? (
      <button
        className="button-primary"
        onClick={() =>
          handleClick(
            ["Create"],
            <StudiesEdit
              studyId={0}
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
        <Navbar
          active="Studies"
          flashMessage={flashMessage}
          goBack={goBack}
          handleClick={handleClick}
        />
        <div className="page-content bg-white">
          <div style={{ position: "relative", height: "100%", width: "100%" }}>
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
      </div>
    );
  }
}

export default Studies;
