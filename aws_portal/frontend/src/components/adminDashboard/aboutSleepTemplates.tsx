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
    const create = getAccess(1, "Create", "About Sleep Templates")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    const edit = getAccess(1, "Edit", "About Sleep Templates")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    const archive = getAccess(1, "Archive", "About Sleep Templates")
      .then(() => this.setState({ canArchive: true }))
      .catch(() => this.setState({ canArchive: false }));

    const aboutSleepTemplates = makeRequest(
      "/admin/about-sleep-template?app=1"
    ).then((aboutSleepTemplates) => this.setState({ aboutSleepTemplates }));

    Promise.all([create, edit, archive, aboutSleepTemplates]).then(() =>
      this.setState({ loading: false })
    );
  }

  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, canArchive, aboutSleepTemplates } = this.state;

    return aboutSleepTemplates.map((s: AboutSleepTemplate) => {
      const { id, name } = s;

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

  delete = (id: number): void => {
    const body = { app: 1, id };
    const opts = { method: "POST", body: JSON.stringify(body) };
    const msg = "Are you sure you want to archive this about sleep template?";

    if (confirm(msg))
      makeRequest("/admin/about-sleep-template/archive", opts)
        .then(this.handleSuccess)
        .catch(this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    this.setState({ loading: true });
    flashMessage(<span>{res.msg}</span>, "success");
    makeRequest("/admin/about-sleep-template?app=1").then(
      (aboutSleepTemplates) =>
        this.setState({ aboutSleepTemplates, loading: false })
    );
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
