import * as React from "react";
import { Component } from "react";
import AccountsEdit from "./accountsEdit";
import { Column, TableData } from "../table/table";
import Table from "../table/table";
import Navbar from "./navbar";
import { makeRequest } from "../../utils";
import { Account } from "../../interfaces";
import { SmallLoader } from "../loader";

interface AccountsProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface AccountsState {
  accounts: Account[];
  columns: Column[];
  loading: boolean;
}

class Accounts extends React.Component<AccountsProps, AccountsState> {
  state = {
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

  componentDidMount() {
    makeRequest("/admin/account?app=1").then((accounts) =>
      this.setState({ accounts, loading: false })
    );
  }

  getData = (): TableData[][] => {
    const dateOptions: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "short",
      day: "numeric"
    };

    return this.state.accounts.map((a: Account) => {
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
              <button
                className="button-secondary"
                onClick={() =>
                  this.props.handleClick(
                    ["Edit", name],
                    <AccountsEdit accountId={id} />,
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
    const { columns, loading, fading } = this.state;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Accounts" />
        <div className="page-content bg-white">
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
                      <AccountsEdit accountId={0} />,
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
    );
  }
}

export default Accounts;
