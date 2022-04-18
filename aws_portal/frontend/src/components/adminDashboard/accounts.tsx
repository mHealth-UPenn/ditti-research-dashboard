import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";

interface AccountsProps {
  handleClick: (
    name: string,
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

// interface AccountsState {}

class Accounts extends React.Component<AccountsProps, any> {
  render() {
    const { handleClick } = this.props;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Accounts" />
        <div className="page-content bg-white">
          <div>Accounts!</div>
        </div>
      </div>
    );
  }
}

export default Accounts;
