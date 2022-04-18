import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";

interface AppsProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

// interface AppsState {}

class Apps extends React.Component<AppsProps, any> {
  render() {
    const { handleClick } = this.props;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Apps" />
        <div className="page-content bg-white">
          <div>Apps!</div>
        </div>
      </div>
    );
  }
}

export default Apps;
