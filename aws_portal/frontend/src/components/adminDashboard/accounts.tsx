import * as React from "react";
import { Component } from "react";
import AccountsEdit from "./accountsEdit";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import Navbar from "./navbar";
import { getAccess, makeRequest } from "../../utils";
import { Account, ResponseBody, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";

/**
 * canCreate: whether the user has permissions to create
 * canEdit: whether the user has permissions to edit
 * canArchive: whether the user permissions to archive
 * accounts: an array of rows to display in the table
 * columns: an array of columns to display in the table
 * loading: whether to display the loading screen
 */
interface AccountsState {
  canCreate: boolean;
  canEdit: boolean;
  canArchive: boolean;
  accounts: Account[];
  columns: Column[];
  loading: boolean;
}

class Accounts extends React.Component<ViewProps, AccountsState> {
  state = {
    canCreate: false,
    canEdit: false,
    canArchive: false,
    accounts: [],
    columns: [
      {
        name: "Name",
        searchable: true,
        sortable: true,
        width: 20
      },
      {
        name: "Email",
        searchable: true,
        sortable: true,
        width: 25
      },
      {
        name: "Phone Number",
        searchable: true,
        sortable: true,
        width: 15
      },
      {
        name: "Created On",
        searchable: false,
        sortable: true,
        width: 15
      },
      {
        name: "Last Login",
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
    loading: true,
    fading: false
  };

  async componentDidMount() {

    // check whether the user has permission to create
    const create = getAccess(1, "Create", "Accounts")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    // check whether the user has permissions to edit
    const edit = getAccess(1, "Edit", "Accounts")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    // check whether the user has permissions to archive
    const archive = getAccess(1, "Archive", "Accounts")
      .then(() => this.setState({ canArchive: true }))
      .catch(() => this.setState({ canArchive: false }));

    // get the table's data
    const accounts = makeRequest("/admin/account?app=1").then((accounts) =>
      this.setState({ accounts })
    );

    // when all requests are complete, hide the loading screen
    Promise.all([create, edit, archive, accounts]).then(() =>
      this.setState({ loading: false })
    );
  }

  /**
   * Get the table's contents
   * @returns The table's contents, consisting of rows of table cells
   */
  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, canArchive, accounts } = this.state;

    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric"
    };

    // iterate over the table's rows
    return accounts.map((a: Account) => {
      const {
        createdOn,
        email,
        firstName,
        id,
        lastLogin,
        lastName,
        phoneNumber
      } = a;
      const name = firstName + " " + lastName;

      // the number of days since the user's last login
      const ago = Math.floor(
        Math.abs(new Date().getTime() - new Date(lastLogin).getTime()) /
          (1000 * 60 * 60 * 24)
      );

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
            <div className="flex-left table-data">
              <span>{email}</span>
            </div>
          ),
          searchValue: email,
          sortValue: email
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>{phoneNumber}</span>
            </div>
          ),
          searchValue: phoneNumber,
          sortValue: phoneNumber
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {new Date(createdOn).toLocaleDateString("en-US", dateOptions)}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: createdOn
        },
        {
          contents: (
            <div className="flex-left table-data">
              <span>
                {lastLogin
                  ? ago
                    ? `${ago} day${ago === 1 ? "" : "s"} ago`
                    : "Today"
                  : "Never"}
              </span>
            </div>
          ),
          searchValue: "",
          sortValue: ""
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
                      <AccountsEdit
                        accountId={id}
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
    const msg = "Are you sure you want to archive this account?";

    if (confirm(msg))
      makeRequest("/admin/account/archive", opts)
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
    makeRequest("/admin/account?app=1").then((accounts) =>
      this.setState({ accounts, loading: false })
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
            <AccountsEdit
              accountId={0}
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
          active="Accounts"
          flashMessage={flashMessage}
          goBack={goBack}
          handleClick={handleClick}
        />
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

export default Accounts;
