import * as React from "react";
import { Component } from "react";
import {
  AboutSleepTemplate,
  ResponseBody,
  Study,
  ViewProps
} from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import Table, { Column, TableData } from "../table/table";
import Navbar from "./navbar";
import AboutSleepTemplatesEdit from "./aboutSleepTemplatesEdit";
import { SmallLoader } from "../loader";

/**
 * canCreate: whether the user has permissions to create
 * canEdit: whether the user has permissions to edit
 * canArchive: whether the user permissions to archive
 * aboutSleepTemplates: an array of rows to display in the table
 * columns: an array of columns to display in the table
 * loading: whether to display the loading screen
 */
interface AboutSleepTemplatesState {
  canCreate: boolean;
  canEdit: boolean;
  canArchive: boolean;
  aboutSleepTemplates: AboutSleepTemplate[];
  columns: Column[];
  loading: boolean;
}

class AboutSleepTemplates extends React.Component<
  ViewProps,
  AboutSleepTemplatesState
> {
  state = {
    canCreate: false,
    canEdit: false,
    canArchive: false,
    aboutSleepTemplates: [],
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
    ],
    loading: true
  };

  async componentDidMount() {

    // check whether the user has permission to create
    const create = getAccess(1, "Create", "About Sleep Templates")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    // check whether the user has permissions to edit
    const edit = getAccess(1, "Edit", "About Sleep Templates")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    // check whether the user has permissions to archive
    const archive = getAccess(1, "Archive", "About Sleep Templates")
      .then(() => this.setState({ canArchive: true }))
      .catch(() => this.setState({ canArchive: false }));

    // get the table's data
    const aboutSleepTemplates = makeRequest(
      "/admin/about-sleep-template?app=1"
    ).then((aboutSleepTemplates) => this.setState({ aboutSleepTemplates }));

    // when all requests are complete, hide the loading screen
    Promise.all([create, edit, archive, aboutSleepTemplates]).then(() =>
      this.setState({ loading: false })
    );
  }

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, canArchive, aboutSleepTemplates } = this.state;

    // iterate over the table's rows
    return aboutSleepTemplates.map((s: AboutSleepTemplate) => {
      const { id, name } = s;

      // map each row to a set of cells for each table column
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
              {canEdit ? (
                <button
                  className="button-secondary"
                  onClick={() =>
                    handleClick(
                      ["Edit", name],
                      <AboutSleepTemplatesEdit
                        aboutSleepTemplateId={id}
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
              {canArchive ? (
                <button
                  className="button-danger"
                  onClick={() => this.delete(id)}
                >
                  Archive
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

  /**
   * Delete a table entry and archive it in the database
   * @param id - the entry's database primary key
   */
  delete = (id: number): void => {

    // prepare the request
    const body = { app: 1, id };  // Admin Dashboard = 1
    const opts = { method: "POST", body: JSON.stringify(body) };

    // confirm deletion
    const msg = "Are you sure you want to archive this about sleep template?";

    if (confirm(msg))
      makeRequest("/admin/about-sleep-template/archive", opts)
        .then(this.handleSuccess)
        .catch(this.handleFailure);
  };

  /**
   * Handle a successful response
   * @param res - the response body
   */
  handleSuccess = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    // show the loading screen
    this.setState({ loading: true });
    flashMessage(<span>{res.msg}</span>, "success");

    // refresh the table's data
    makeRequest("/admin/about-sleep-template?app=1").then(
      (aboutSleepTemplates) =>
        this.setState({ aboutSleepTemplates, loading: false })
    );
  };

  /**
   * Handle a failed response
   * @param res - the response body
   */
  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    // flash the message returned from the endpoint or "Internal server error"
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

    // if the user has permission to create, show the create button
    const tableControl = canCreate ? (
      <button
        className="button-primary"
        onClick={() =>
          handleClick(
            ["Create"],
            <AboutSleepTemplatesEdit
              aboutSleepTemplateId={0}
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
          active="About Sleep Templates"
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

export default AboutSleepTemplates;
