import * as React from "react";
import { Component } from "react";
import AccountsEdit from "./accountsEdit";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import Navbar from "./navbar";
import { getAccess, makeRequest } from "../../utils";
import { Account, ViewProps } from "../../interfaces";
import { SmallLoader } from "../loader";

interface AccountsState {
  canCreate: boolean;
  canEdit: boolean;
  accounts: Account[];
  columns: Column[];
  loading: boolean;
}

class Accounts extends React.Component<ViewProps, AccountsState> {
  state = {
    canCreate: false,
    canEdit: false,
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
    const create = getAccess(1, "Create", "Accounts")
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    const edit = getAccess(1, "Edit", "Accounts")
      .then(() => this.setState({ canEdit: true }))
      .catch(() => this.setState({ canEdit: false }));

    const accounts = makeRequest("/admin/account?app=1").then((accounts) =>
      this.setState({ accounts })
    );

    Promise.all([create, edit, accounts]).then(() =>
      this.setState({ loading: false })
    );
  }

  getData = (): TableData[][] => {
    const { flashMessage, goBack, handleClick } = this.props;
    const { canEdit, accounts } = this.state;

    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric"
    };

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
      const ago = Math.floor(
        Math.abs(new Date().getTime() - new Date(lastLogin).getTime()) /
          (1000 * 60 * 60 * 24)
      );

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
    const { flashMessage, goBack, handleClick } = this.props;
    const { canCreate, columns, loading } = this.state;

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
