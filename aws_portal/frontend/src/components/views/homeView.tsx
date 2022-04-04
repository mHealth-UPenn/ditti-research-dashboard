import * as React from "react";
import { Component } from "react";

interface HomeViewProps {
  apps: { name: string; id: string }[];
}

// interface HomeViewState {}

class HomeView extends React.Component<any, HomeViewProps> {
  // state = { :  }
  render() {
    return (
      <div className="bg-white">
        {this.props.apps.map((a: { name: string; id: string }) => a.name)}
      </div>
    );
  }
}

export default HomeView;
