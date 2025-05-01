import * as React from "react";
import { LoaderProps, FullLoaderProps } from "./loader.types";

const Loader = ({ style, msg }: LoaderProps) => {
  return (
    <div id="loader" style={style}>
      <div className="lds-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      {msg ? <span>{msg}</span> : null}
    </div>
  );
};

export const SmallLoader = () => {
  return (
    <div className="loader-container">
      <Loader style={{}} />
    </div>
  );
};

export const FullLoader = ({ loading, msg }: FullLoaderProps) => {
  const loadingStyle: React.CSSProperties = {
    alignItems: "center",
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
    justifyContent: "center",
    height: "100%",
    position: "absolute",
    width: "100%",
    zIndex: 100,
  };

  const fadingStyle: React.CSSProperties = {
    alignItems: "center",
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
    justifyContent: "center",
    height: "100%",
    opacity: 0,
    position: "absolute",
    transition: "opacity 500ms ease-in",
    width: "100%",
    pointerEvents: "none",
    zIndex: 100,
  };

  const style = loading ? loadingStyle : fadingStyle;
  return <Loader style={style} msg={msg} />;
};
