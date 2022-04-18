import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";

interface AccessGroupsProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

// interface AccessGroupsState {}

class AccessGroups extends React.Component<AccessGroupsProps, any> {
  render() {
    const { handleClick } = this.props;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Access Groups" />
        <div className="page-content bg-white">
          <div>AccessGroups!</div>
        </div>
      </div>
    );
  }
}

export default AccessGroups;
