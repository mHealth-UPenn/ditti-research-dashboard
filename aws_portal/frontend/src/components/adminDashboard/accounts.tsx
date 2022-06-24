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
        width: 25
      },
      {
        name: "Email",
        searchable: true,
        sortable: true,
        width: 35
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
    // const pad = Math.max(...accounts.map((a) => String(a.lastLogin).length));

    return this.state.accounts.map((a: Account) => {
      const { createdOn, email, firstName, id, lastLogin, lastName } = a;
      const name = firstName + " " + lastName;

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
              {/* <span>{createdOn.toDateString()}</span> */}
              <span>{createdOn}</span>
            </div>
          ),
          searchValue: "",
          sortValue: createdOn
          // sortValue: String(createdOn.getTime())
        },
        {
          contents: (
            <div className="flex-left table-data">
              {/* <span>
                {lastLogin
                  ? `${lastLogin} day${lastLogin === 1 ? "" : "s"} ago`
                  : "Today"}
              </span> */}
              <span>{lastLogin}</span>
            </div>
          ),
          searchValue: "",
          sortValue: ""
          // sortValue: String(lastLogin).padStart(pad, "0")
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
