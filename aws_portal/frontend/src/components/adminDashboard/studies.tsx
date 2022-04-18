import * as React from "react";
import { Component } from "react";
import Navbar from "./navbar";

interface StudiesProps {
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

// interface StudiesState {}

class Studies extends React.Component<StudiesProps, any> {
  render() {
    const { handleClick } = this.props;

    return (
      <div className="page-container">
        <Navbar handleClick={handleClick} active="Studies" />
        <div className="page-content bg-white">
          <div>Studies!</div>
        </div>
      </div>
    );
  }
}

export default Studies;
