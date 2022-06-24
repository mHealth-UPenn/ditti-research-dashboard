import * as React from "react";
import { Component } from "react";

interface LoaderStyle {
  alignItems: string;
  backgroundColor: string;
  display: string;
  justifyContent: string;
  height: string;
  position: string;
  width: string;
}

interface LoaderProps {
  style: LoaderStyle;
}

interface FullLoaderProps {
  loading: boolean;
}

interface FullLoaderState {
  loadingStyle: LoaderStyle;
  fadingStyle: LoaderStyle;
}

class Loader extends React.Component<LoaderProps, any> {
  render() {
    return (
      <div
        id="loader"
        style={this.props.style as React.StyleHTMLAttributes<HTMLDivElement>}
      >
        <div className="lds-ring">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
      </div>
    );
  }
}

export class SmallLoader extends React.Component<
  FullLoaderProps,
  FullLoaderState
> {
  state = {
    loadingStyle: {
      alignItems: "center",
      backgroundColor: "white",
      display: "flex",
      justifyContent: "center",
      height: "100%",
      position: "absolute",
      width: "100%"
    },
    fadingStyle: {
      alignItems: "center",
      backgroundColor: "white",
      display: "flex",
      justifyContent: "center",
      height: "100%",
      opacity: 0,
      position: "absolute",
      transition: "opacity 500ms ease-in",
      width: "100%"
    }
  };

  render() {
    const { loadingStyle, fadingStyle } = this.state;
    const style = this.props.loading ? loadingStyle : fadingStyle;
    return <Loader style={style} />;
  }
}

export class FullLoader extends React.Component<
  FullLoaderProps,
  FullLoaderState
> {
  state = {
    loadingStyle: {
      alignItems: "center",
      backgroundColor: "white",
      display: "flex",
      justifyContent: "center",
      height: "100%",
      position: "absolute",
      width: "100%"
    },
    fadingStyle: {
      alignItems: "center",
      backgroundColor: "white",
      display: "flex",
      justifyContent: "center",
      height: "100%",
      opacity: 0,
      position: "absolute",
      transition: "opacity 500ms ease-in",
      width: "100%"
    }
  };

  render() {
    const { loadingStyle, fadingStyle } = this.state;
    const style = this.props.loading ? loadingStyle : fadingStyle;
    return <Loader style={style} />;
  }
}
