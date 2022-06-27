import * as React from "react";
import { Component } from "react";

interface LoaderProps {
  style: React.CSSProperties;
}

interface SmallLoaderState {
  style: React.CSSProperties;
}

interface FullLoaderProps {
  loading: boolean;
}

interface FullLoaderState {
  loadingStyle: React.CSSProperties;
  fadingStyle: React.CSSProperties;
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

export class SmallLoader extends React.Component<any, any> {
  render() {
    return (
      <div className="loader-container">
        <Loader style={{}} />
      </div>
    );
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
    } as React.CSSProperties,
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
    } as React.CSSProperties
  };

  render() {
    const { loadingStyle, fadingStyle } = this.state;
    const style = this.props.loading ? loadingStyle : fadingStyle;
    return <Loader style={style} />;
  }
}
