import * as React from "react";
import { Component } from "react";

interface AccountsEditProps {
  accountId: number;
}

interface AccountsEditState {
  name: string;
  email: string;
  accessGroups: {
    id: number;
    name: string;
    permissions: {
      id: number;
      name: string;
    }[];
  }[];
  studies: {
    id: number;
    name: string;
    role: {
      id: number;
      name: string;
      permissions: string[];
    };
  }[];
}

class AccountsEdit extends React.Component<
  AccountsEditProps,
  AccountsEditState
> {
  constructor(props: AccountsEditProps) {
    super(props);

    const { accountId } = props;
    this.state = accountId
      ? this.getData(accountId)
      : {
          name: "",
          email: "",
          accessGroups: [],
          studies: []
        };
  }

  getData(id: number) {
    return {
      name: "",
      email: "",
      accessGroups: [],
      studies: []
    };
  }

  render() {
    return <p>Create Account</p>;
  }
}

export default AccountsEdit;
